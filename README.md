# Projet RFID - Gestion des Employés

Application Flask pour la gestion des employés avec système RFID, utilisant PostgreSQL comme base de données.

## Configuration

### Base de données PostgreSQL

L'application se connecte à une base de données PostgreSQL distante. Les paramètres de connexion sont configurés dans `config.py` :

- **Host**: 51.20.7.106
- **Database**: rfid1
- **User**: akram
- **Port**: 5432

### Schéma de la base de données

- **Table `userinterface`**: Gestion des utilisateurs (id_user, username, password, approve)
- **Table `employe`**: Informations des employés (id_employe, nom, prenom, carte_rfid)
- **Table `historique`**: Historique des entrées/sorties (id_historique, id_employe, date_entree, date_sortie)

## Installation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

2. Configurer la base de données dans `config.py`

3. Lancer l'application :
```bash
python app1.py
```

Ou utiliser le fichier batch :
```bash
start_app1.bat
```

## Accès

- **URL locale**: http://localhost:5000
- **URL réseau**: http://0.0.0.0:5000

## Fonctionnalités

- Authentification utilisateur
- Gestion des employés (ajout, modification, suppression)
- Suivi des entrées/sorties via RFID
- Historique des présences
- Export Excel de l'historique
- Interface administrateur pour approuver les utilisateurs

## Technologies

- **Backend**: Flask (Python)
- **Base de données**: PostgreSQL
- **Bibliothèques**: psycopg2, pandas, xlsxwriter

