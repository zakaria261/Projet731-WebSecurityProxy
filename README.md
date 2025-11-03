## Installation

1.  **Cloner le dépôt :**
    ```bash
    git clone <URL_DE_VOTRE_DEPOT>
    cd Projet731
    ```

2.  **Créer et activer un environnement virtuel :**
    ```bash
    python3 -m venv venv
    source venv/bin/activate # Sur Linux/macOS
    # .\venv\Scripts\activate # Sur Windows
    ```

3.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```


    ## Utilisation

Assurez-vous que l'environnement virtuel est activé avant de lancer les commandes suivantes.

1.  **Démarrer le Proxy de Destination (Terminal 1) :**
    ```bash
    python -m web_security_proxy.proxy_destination.server_proxy
    ```

2.  **Démarrer le Proxy Source (Terminal 2) :**
    ```bash
    python -m web_security_proxy.proxy_source.client_proxy
    ```

3.  **Lancer les tests de performance et de connectivité (Terminal 3) :**
    ```bash
    python web_security_proxy/test/test_proxy_sites.py
    ```

4.  **(Optionnel) Configurer votre navigateur :**
    *   Hôte HTTP Proxy : `127.0.0.1`
    *   Port HTTP Proxy : `8080`
