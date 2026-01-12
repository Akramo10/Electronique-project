@echo off
echo Configuration des variables d'environnement...
set MYSQL_HOST=localhost
set MYSQL_USER=root
set MYSQL_PASSWORD=
set MYSQL_DB=rfid1
set SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

echo Demarrage de l'application Flask (app1.py)...
python app1.py

pause

