# Proxy de Sécurité Web

## 📋 Description
Système de double proxy avec chiffrement de bout en bout du trafic HTTP.

## 🏗️ Architecture
- **Proxy Source** : Reçoit les requêtes du navigateur, les chiffre
- **Proxy Destination** : Déchiffre, fait les requêtes au web, renvoie chiffré

## 🔐 Sécurité
- **Échange de clés** : RSA-2048 (OAEP + SHA-256)
- **Chiffrement des données** : AES-256-GCM
- **Authentification** : Intégrée via GCM

## 🚀 Installation
```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Installer les dépendances
pip install cryptography requests
```

## ▶️ Utilisation

### 1. Démarrer le Proxy de Destination
```bash
python -m web_security_proxy.proxy_destination.server_proxy
```

### 2. Démarrer le Proxy Source
```bash
python -m web_security_proxy.proxy_source.client_proxy
```

### 3. Configurer le navigateur
- Paramètres proxy HTTP : `127.0.0.1:8080`

### 4. Tester
```bash
python test/test_proxy_sites.py
```

## 📊 Performances

[Ajoutez ici vos résultats après avoir lancé les tests]

- **Latence ajoutée** : ~X ms
- **Dégradation du débit** : ~X%
- **Sites testés avec succès** : X/Y

## ⚠️ Limitations
- Supporte uniquement HTTP (pas HTTPS natif)
- Pas de cache implémenté
- Handshake RSA à chaque connexion

## 👨‍💻 Auteur
[Votre nom] - [Date]