# Guide de Déploiement sur Ubuntu/Linux

## Prérequis

- Ubuntu 20.04+ ou distribution Linux similaire
- Python 3.8+
- Accès à la base de données PostgreSQL distante

## Installation

### 1. Mise à jour du système

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Installation de Python et pip

```bash
sudo apt install -y python3 python3-pip python3-venv
```

### 3. Cloner le projet (si pas déjà fait)

```bash
git clone https://github.com/Akramo10/Electronique-project.git
cd Electronique-project
```

### 4. Créer un environnement virtuel Python

```bash
python3 -m venv venv
```

### 5. Activer l'environnement virtuel

```bash
source venv/bin/activate
```

Vous devriez voir `(venv)` apparaître devant votre prompt.

### 6. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 7. Configuration

Créer le fichier `config.py` à partir de l'exemple :

```bash
cp config.py.example config.py
```

Puis éditer `config.py` avec vos paramètres PostgreSQL :

```python
import secrets

SECRET_KEY = secrets.token_hex(16)

# Configuration PostgreSQL distante
POSTGRES_HOST = "51.20.7.106"
POSTGRES_USER = "akram"
POSTGRES_PASSWORD = "AWS-Stage"
POSTGRES_DB = "rfid1"
POSTGRES_PORT = 5432
```

### 8. Tester l'application

```bash
python3 app1.py
```

L'application devrait démarrer sur `http://0.0.0.0:5000`

## Déploiement en production avec systemd

### 1. Créer un service systemd

Créer le fichier `/etc/systemd/system/rfid-app.service` :

```bash
sudo nano /etc/systemd/system/rfid-app.service
```

Contenu du fichier :

```ini
[Unit]
Description=RFID Flask Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Electronique-project
Environment="PATH=/home/ubuntu/Electronique-project/venv/bin"
ExecStart=/home/ubuntu/Electronique-project/venv/bin/python3 /home/ubuntu/Electronique-project/app1.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Important** : Remplacez `/home/ubuntu/Electronique-project` par le chemin réel de votre projet.

### 2. Activer et démarrer le service

```bash
sudo systemctl daemon-reload
sudo systemctl enable rfid-app
sudo systemctl start rfid-app
```

### 3. Vérifier le statut

```bash
sudo systemctl status rfid-app
```

### 4. Voir les logs

```bash
sudo journalctl -u rfid-app -f
```

## Utilisation avec Gunicorn (recommandé pour la production)

### 1. Installer Gunicorn

```bash
source venv/bin/activate
pip install gunicorn
```

### 2. Créer un fichier de configuration Gunicorn

Créer `gunicorn_config.py` :

```python
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
```

### 3. Modifier le service systemd pour utiliser Gunicorn

Modifier `/etc/systemd/system/rfid-app.service` :

```ini
[Unit]
Description=RFID Flask Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Electronique-project
Environment="PATH=/home/ubuntu/Electronique-project/venv/bin"
ExecStart=/home/ubuntu/Electronique-project/venv/bin/gunicorn -c gunicorn_config.py app1:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. Recharger et redémarrer

```bash
sudo systemctl daemon-reload
sudo systemctl restart rfid-app
```

## Configuration du pare-feu

Si vous utilisez UFW :

```bash
sudo ufw allow 5000/tcp
```

## Script de démarrage rapide

Créer un fichier `start.sh` :

```bash
#!/bin/bash
cd /home/ubuntu/Electronique-project
source venv/bin/activate
python3 app1.py
```

Rendre exécutable :

```bash
chmod +x start.sh
```

## Dépannage

### Vérifier que l'environnement virtuel est activé

```bash
which python3
# Devrait afficher : /home/ubuntu/Electronique-project/venv/bin/python3
```

### Vérifier les dépendances installées

```bash
source venv/bin/activate
pip list
```

### Tester la connexion PostgreSQL

```bash
source venv/bin/activate
python3 -c "import psycopg2; from config import POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT; conn = psycopg2.connect(host=POSTGRES_HOST, user=POSTGRES_USER, password=POSTGRES_PASSWORD, database=POSTGRES_DB, port=POSTGRES_PORT); print('Connexion OK'); conn.close()"
```

