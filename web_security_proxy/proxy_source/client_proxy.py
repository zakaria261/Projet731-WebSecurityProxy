import socket
import threading
import sys
from cryptography import exceptions as crypto_exceptions

from web_security_proxy.config.settings import (
    SOURCE_PROXY_HOST, SOURCE_PROXY_PORT, 
    DESTINATION_PROXY_HOST, DESTINATION_PROXY_PORT, 
    BUFFER_SIZE
)
from .crypto_client import (
    load_public_key, 
    generate_and_encrypt_session_key, 
    encrypt_data, 
    decrypt_data
)

def get_request_headers(client_socket):
    """Récupère la requête HTTP complète du navigateur."""
    data = b""
    while True:
        try:
            chunk = client_socket.recv(BUFFER_SIZE)
            if not chunk: 
                return None
            data += chunk
            if b'\r\n\r\n' in data: 
                return data
        except socket.error: 
            return None

def initiate_secure_handshake(target_socket):
    """Etablit une connexion sécurisée avec le proxy de sortie."""
    
    target_socket.sendall(b"PROXY_SECURITY_HELLO\r\n") 
    
    pem_data = b""
    while True:
        chunk = target_socket.recv(BUFFER_SIZE)
        if not chunk:
            raise Exception("Connexion interrompue lors de l'echange de cle.")
        pem_data += chunk
        if b'-----END PUBLIC KEY-----\n' in pem_data:
            break
    
    load_public_key(pem_data)
    
    encrypted_session_key, session_key = generate_and_encrypt_session_key()
    
    key_transmission = b"ENCRYPTED_SESSION_KEY:" + encrypted_session_key + b":END_KEY\r\n"
    target_socket.sendall(key_transmission)
    
    return session_key

def handle_browser_connection(browser_socket):
    """Gère une connexion entrante du navigateur."""
    target_socket = None
    session_key = None
    
    try:
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.settimeout(30)
        target_socket.connect((DESTINATION_PROXY_HOST, DESTINATION_PROXY_PORT))
        
        session_key = initiate_secure_handshake(target_socket)
        
        raw_http_request = get_request_headers(browser_socket) 
        if not raw_http_request: 
            return

        encrypted_request = encrypt_data(raw_http_request, session_key) 
        target_socket.sendall(encrypted_request)

        target_socket.settimeout(5)
        
        while True:
            try:
                encrypted_response_chunk = target_socket.recv(BUFFER_SIZE)
                if not encrypted_response_chunk:
                    break
                
                try:
                    decrypted_response = decrypt_data(encrypted_response_chunk, session_key)
                    browser_socket.sendall(decrypted_response)
                except crypto_exceptions.InvalidTag:
                    print("Erreur: donnees corrompues detectees")
                    break
                    
            except socket.timeout:
                break
            except socket.error:
                break
            
    except crypto_exceptions.InvalidTag:
        print("Erreur: verification de l'integrite des donnees echouee")
    except socket.timeout:
        print("Erreur: delai de connexion depasse")
    except socket.error as e:
        print(f"Erreur socket: {e}")
    except Exception as e:
        print(f"Erreur: {e}")
        
    finally:
        if target_socket: 
            target_socket.close()
        browser_socket.close()

def start_proxy():
    """Démarre le proxy source."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((SOURCE_PROXY_HOST, SOURCE_PROXY_PORT))
    except socket.error as e:
        print(f"Impossible de demarrer le proxy sur le port {SOURCE_PROXY_PORT}: {e}")
        sys.exit(1)
        
    server_socket.listen(5) 
    print(f"Proxy source demarre sur {SOURCE_PROXY_HOST}:{SOURCE_PROXY_PORT}")
    
    while True:
        try:
            browser_socket, addr = server_socket.accept()
            client_handler = threading.Thread(
                target=handle_browser_connection, 
                args=(browser_socket,)
            )
            client_handler.daemon = True
            client_handler.start()
        except KeyboardInterrupt:
            print("\nArret du proxy source")
            break
        except Exception as e:
            print(f"Erreur: {e}")
            
    server_socket.close()

if __name__ == "__main__":
    start_proxy()