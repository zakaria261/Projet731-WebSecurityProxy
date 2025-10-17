/web_security_proxy
├── proxy_source/
│   ├── client_proxy.py         # Le cœur du Proxy Source (écoute du navigateur, CHIFFRE, envoie)
│   ├── __init__.py             # Module Python
│   └── crypto_client.py        # Fonctions de gestion de clé (RSA) et chiffrement symétrique
│
├── proxy_destination/
│   ├── server_proxy.py         # Le cœur du Proxy de Sortie (écoute du client_proxy, DÉCHIFFRE, relaye au web)
│   ├── __init__.py             # Module Python
│   └── crypto_server.py        # Fonctions de gestion de clé (RSA) et déchiffrement symétrique
│
├── config/
│   ├── keys/                   # Dossier pour stocker les clés RSA (si générées hors ligne)
│   │   ├── destination_public.pem
│   │   └── destination_private.pem
│   └── settings.py             # Fichier de configuration (ports, hôtes, algorithmes choisis)
│
├── test/
│   ├── performance_test.py     # Script pour mesurer le débit et la latence (Étape 4)
│   └── functional_test.py      # Script de test de base
│
└── README.md                   # Documentation du projet