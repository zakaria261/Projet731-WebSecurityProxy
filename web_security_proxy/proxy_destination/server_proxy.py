
import socket
import threading
import sys
from urllib.parse import urlparse
from cryptography import exceptions as crypto_exceptions

from web_security_proxy.config.settings import DESTINATION_PROXY_HOST, DESTINATION_PROXY_PORT, BUFFER_SIZE
from .crypto_server import generate_rsa_keys, decrypt_session_key, encrypt_data, decrypt_data

def handle_proxy_client(client_socket):
    """Gère la connexion du Proxy Source."""
    target_socket = None
    
    try:
        
        hello = client_socket.recv(BUFFER_SIZE)
        if b"PROXY_SECURITY_HELLO" not in hello:
            raise Exception("Protocole de poignée de main invalide.")
        
        print("[*] Message HELLO reçu du Proxy Source.")
        
        from .crypto_server import PUBLIC_KEY_SERIALIZED
        client_socket.sendall(PUBLIC_KEY_SERIALIZED)
        print("[*] Clé publique RSA envoyée.")
        
        encrypted_key_data = b""
        while True:
            chunk = client_socket.recv(BUFFER_SIZE)
            if not chunk:
                raise Exception("Connexion fermée avant la réception de la clé de session.")
            encrypted_key_data += chunk
            if b":END_KEY" in encrypted_key_data:
                break
        
        start_idx = encrypted_key_data.find(b"ENCRYPTED_SESSION_KEY:") + len(b"ENCRYPTED_SESSION_KEY:")
        end_idx = encrypted_key_data.find(b":END_KEY")
        encrypted_session_key = encrypted_key_data[start_idx:end_idx]
        
        session_key = decrypt_session_key(encrypted_session_key)
        print("[*] Clé de session déchiffrée et établie.")
        

            
        encrypted_request = client_socket.recv(BUFFER_SIZE)
        if not encrypted_request:
            return
        
        # Déchiffrement de la requête
        try:
            decrypted_request = decrypt_data(encrypted_request, session_key)
        except crypto_exceptions.InvalidTag:
            print("[!!!] ALERTE SÉCURITÉ : Requête altérée ou clé invalide détectée.")
            return
        
        print(f"[*] Requête déchiffrée ({len(decrypted_request)} octets).")
        
        # 6. Extraction de l'URL cible depuis la requête HTTP
        target_host, target_port, request_path = parse_http_request(decrypted_request)
        
        # 7. Connexion au serveur web cible
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.settimeout(15)  # Timeout de 15 secondes
        target_socket.connect((target_host, target_port))
        print(f"[*] Connecté au serveur web : {target_host}:{target_port}")
        
        # 8. Envoi de la requête au serveur web
        target_socket.sendall(decrypted_request)
        
        # 9. Relais de la réponse (Réception, CHIFFREMENT, Renvoi au Proxy Source)
        # CORRECTION: Amélioration de la lecture complète de la réponse
        target_socket.settimeout(2)  # 2 secondes entre chaque chunk
        
        total_bytes = 0
        while True:
            try:
                response_chunk = target_socket.recv(BUFFER_SIZE)
                if not response_chunk:
                    break
                
                total_bytes += len(response_chunk)
                
                # CHIFFREMENT de la réponse
                encrypted_response = encrypt_data(response_chunk, session_key)
                
                # Envoi au Proxy Source
                client_socket.sendall(encrypted_response)
                
            except socket.timeout:
                # Fin normale de la transmission
                break
            except socket.error as e:
                print(f"[!] Erreur lors du relais : {e}")
                break
        
        if target_socket:
            target_socket.close()
        print(f"[*] Relais de la réponse terminé ({total_bytes} octets transférés).")
        
    except crypto_exceptions.InvalidTag:
        print("[!!!] ALERTE SÉCURITÉ : Trafic altéré ou clé invalide.")
    except socket.timeout:
        print("[!] Timeout lors de la connexion au serveur web.")
    except socket.error as e:
        print(f"[!] Erreur de socket : {e}")
    except Exception as e:
        print(f"[!] Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()
    finally:
        client_socket.close()
        print("[*] Fin de la session du Proxy de Sortie.")

def parse_http_request(request_data):
    """Extrait l'hôte, le port et le chemin de la requête HTTP."""
    try:
        request_str = request_data.decode('utf-8', errors='ignore')
        lines = request_str.split('\r\n')
        
        # Extraire la ligne de requête (ex: "GET / HTTP/1.1")
        request_line = lines[0].split()
        request_path = request_line[1] if len(request_line) > 1 else '/'
        
        # Extraire l'hôte depuis les en-têtes
        target_host = None
        target_port = 80
        
        for line in lines[1:]:
            if line.lower().startswith('host:'):
                host_header = line.split(':', 1)[1].strip()
                # CORRECTION: Utiliser rsplit pour gérer les ports correctement
                if ':' in host_header:
                    parts = host_header.rsplit(':', 1)
                    target_host = parts[0]
                    try:
                        target_port = int(parts[1])
                    except ValueError:
                        # Si ce n'est pas un port valide, considérer tout comme hostname
                        target_host = host_header
                        target_port = 80
                else:
                    target_host = host_header
                break
        
        if not target_host:
            raise ValueError("En-tête Host manquant dans la requête HTTP.")
        
        print(f"[*] URL cible extraite : {target_host}:{target_port}{request_path}")
        return target_host, target_port, request_path
        
    except Exception as e:
        print(f"[!] Erreur lors de l'analyse de la requête HTTP : {e}")
        raise

def start_proxy():
    """Point d'entrée du Proxy de Sortie."""
    
    # Générer les clés RSA au démarrage
    generate_rsa_keys()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((DESTINATION_PROXY_HOST, DESTINATION_PROXY_PORT))
    except socket.error as e:
        print(f"[!] Échec de la liaison au port {DESTINATION_PROXY_PORT} : {e}")
        sys.exit(1)
    
    server_socket.listen(5)
    print(f"[*] Proxy de Sortie en écoute sur {DESTINATION_PROXY_HOST}:{DESTINATION_PROXY_PORT}")
    
    while True:
        try:
            client_socket, addr = server_socket.accept()
            print(f"[*] Nouvelle connexion du Proxy Source : {addr}")
            client_handler = threading.Thread(target=handle_proxy_client, args=(client_socket,))
            client_handler.daemon = True
            client_handler.start()
        except KeyboardInterrupt:
            print("\n[*] Arrêt du Proxy de Sortie.")
            break
        except Exception as e:
            print(f"[!] Erreur générale dans la boucle d'acceptation : {e}")
    
    server_socket.close()

if __name__ == "__main__":
    start_proxy()
