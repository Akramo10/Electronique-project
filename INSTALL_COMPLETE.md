# Installation Complète - De Zéro sur Ubuntu

## Étape 1 : Nettoyer l'ancienne installation (si elle existe)

```bash
# Supprimer l'ancien dossier si présent
cd ~
rm -rf Electronique-project
```

## Étape 2 : Cloner le projet depuis GitHub

```bash
# Cloner le dépôt
git clone https://github.com/Akramo10/Electronique-project.git

# Aller dans le dossier
cd Electronique-project
```

## Étape 3 : Installer Python et les outils nécessaires

```bash
# Mettre à jour le système
sudo apt update

# Installer Python 3, pip et venv
sudo apt install -y python3 python3-pip python3-venv
```

## Étape 4 : Créer l'environnement virtuel

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate

# Vous devriez voir (venv) devant votre prompt
```

## Étape 5 : Installer les dépendances

```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances (versions compatibles)
pip install -r requirements.txt

# Vérifier que pandas et numpy sont bien installés
pip list | grep -E "numpy|pandas"
```

Vous devriez voir :
- numpy==2.0.2
- pandas==2.2.2

## Étape 6 : Tester l'import pandas/numpy

```bash
# Tester que tout fonctionne
python3 -c "import pandas as pd; import numpy as np; print('✓ OK: numpy', np.__version__, 'pandas', pd.__version__)"
```

Si vous voyez "✓ OK", continuez. Sinon, réinstallez :

```bash
pip uninstall -y numpy pandas
pip install numpy==2.0.2 pandas==2.2.2
```

## Étape 7 : Configurer la base de données

```bash
# Créer le fichier config.py à partir de l'exemple
cp config.py.example config.py

# Éditer config.py avec vos paramètres PostgreSQL
nano config.py
```

Vérifiez que les paramètres sont corrects :
- POSTGRES_HOST = "51.20.7.106"
- POSTGRES_USER = "akram"
- POSTGRES_PASSWORD = "AWS-Stage"
- POSTGRES_DB = "rfid1"
- POSTGRES_PORT = 5432

## Étape 8 : Tester la connexion PostgreSQL

```bash
# Tester la connexion
python3 -c "import psycopg2; from config import POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT; conn = psycopg2.connect(host=POSTGRES_HOST, user=POSTGRES_USER, password=POSTGRES_PASSWORD, database=POSTGRES_DB, port=POSTGRES_PORT); print('✓ Connexion PostgreSQL OK'); conn.close()"
```

## Étape 9 : Lancer l'application

```bash
# S'assurer que l'environnement virtuel est activé
source venv/bin/activate

# Lancer l'application
python3 app1.py
```

Vous devriez voir :
```
 * Running on http://0.0.0.0:5000
```

## Étape 10 : Tester l'application

Ouvrez un navigateur ou utilisez curl :

```bash
# Tester depuis le serveur
curl http://localhost:5000
```

Ou depuis votre machine locale, ouvrez :
- http://VOTRE_IP_SERVEUR:5000

## Résumé des commandes (copier-coller)

```bash
# 1. Nettoyer
cd ~
rm -rf Electronique-project

# 2. Cloner
git clone https://github.com/Akramo10/Electronique-project.git
cd Electronique-project

# 3. Installer Python
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 4. Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 5. Installer dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 6. Tester pandas/numpy
python3 -c "import pandas as pd; import numpy as np; print('OK')"

# 7. Configurer
cp config.py.example config.py
nano config.py  # Éditer avec vos paramètres

# 8. Tester connexion PostgreSQL
python3 -c "import psycopg2; from config import *; conn = psycopg2.connect(host=POSTGRES_HOST, user=POSTGRES_USER, password=POSTGRES_PASSWORD, database=POSTGRES_DB, port=POSTGRES_PORT); print('OK'); conn.close()"

# 9. Lancer
python3 app1.py
```

## En cas de problème

### Erreur pandas/numpy
```bash
pip uninstall -y numpy pandas
pip install numpy==2.0.2 pandas==2.2.2
```

### Erreur de connexion PostgreSQL
Vérifiez :
- Le serveur PostgreSQL est accessible depuis votre serveur Ubuntu
- Les paramètres dans config.py sont corrects
- Le pare-feu autorise la connexion

### L'application ne démarre pas
Vérifiez que l'environnement virtuel est activé :
```bash
which python3
# Devrait afficher : /home/ubuntu/Electronique-project/venv/bin/python3
```

