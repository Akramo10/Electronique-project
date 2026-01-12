import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_file
from flask_mysqldb import MySQL
import pandas as pd
import io
from datetime import datetime







app = Flask(__name__)







# Configuration de la base de données MySQL
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
mysql = MySQL(app)





# Clé secrète pour sécuriser les sessions
app.secret_key = os.environ.get('SECRET_KEY')





@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error_msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username and password:
            if username == 'ADMIN' and password == 'ADMIN':
                session['loggedin'] = True
                session['id'] = 1
                session['username'] = 'ADMIN'
                return redirect(url_for('ADMIN'))

            cursor = mysql.connection.cursor()
            try:
                cursor.execute('SELECT * FROM userinterface WHERE Username = %s', (username,))
                user = cursor.fetchone()
                if user and user['Password'] == password and user['Approve'] == 1:
                    session['loggedin'] = True
                    session['id'] = user['ID_User']
                    session['username'] = user['Username']
                    return redirect(url_for('dashboard'))
                else:
                    error_msg = 'Nom d\'utilisateur ou mot de passe incorrect!'
            except Exception as e:
                error_msg = 'Une erreur s\'est produite lors de la tentative de connexion.'
                print(f"Database error: {e}")
            finally:
                cursor.close()
        else:
            error_msg = 'Veuillez fournir un nom d\'utilisateur et un mot de passe.'

    return render_template('login.html', error_msg=error_msg)



@app.route('/ADMIN')
def ADMIN():
    if 'loggedin' in session and session['username'] == 'ADMIN':
        cursor = mysql.connection.cursor()
        try:
            cursor.execute('SELECT * FROM userinterface WHERE Approve = 0')
            user_requests = cursor.fetchall()
            return render_template('admin.html', user_requests=user_requests)
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
    return redirect(url_for('login'))

@app.route('/approve_user/<int:user_id>', methods=['GET'])
def approve_user(user_id):
    if 'loggedin' in session and session['username'] == 'ADMIN':
        cursor = mysql.connection.cursor()
        try:
            cursor.execute('UPDATE userinterface SET Approve = 1 WHERE ID_User = %s', (user_id,))
            mysql.connection.commit()
            return redirect(url_for('ADMIN'))
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
    return redirect(url_for('login'))

@app.route('/reject_user/<int:user_id>', methods=['GET'])
def reject_user(user_id):
    if 'loggedin' in session and session['username'] == 'ADMIN':
        cursor = mysql.connection.cursor()
        try:
            cursor.execute('DELETE FROM userinterface WHERE ID_User = %s', (user_id,))
            mysql.connection.commit()
            return redirect(url_for('ADMIN'))
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO userinterface (Username, Password, Approve) VALUES (%s, %s, %s)', (username, password, 0))
        mysql.connection.commit()
        cursor.close()

        return 'Inscription réussie!'

    return render_template('register.html')

@app.route('/logout')
def logout():
    # Supprimer toutes les variables de session
    session.clear()
    # Rediriger vers la page de connexion
    return redirect(url_for('login'))


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    error_msg = ''
    success_msg = ''
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        carte_rfid = request.form.get('carte_rfid')

        if nom and prenom and carte_rfid:
            cursor = mysql.connection.cursor()
            try:
                cursor.execute('INSERT INTO employe (Nom, Prenom, Carte_RFID) VALUES (%s, %s, %s)', (nom, prenom, carte_rfid))
                mysql.connection.commit()
                success_msg = 'Employé ajouté avec succès!'
            except Exception as e:
                error_msg = 'Une erreur s\'est produite lors de l\'ajout de l\'employé.'
                print(f"Database error: {e}")
            finally:
                cursor.close()
        else:
            error_msg = 'Veuillez remplir tous les champs.'

    return render_template('add_employee.html', error_msg=error_msg, success_msg=success_msg)

@app.route('/all_users', methods=['GET', 'POST'])
def all_users():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        search_query = request.form.get('search_query', '')
        query = 'SELECT * FROM employe WHERE Nom LIKE %s OR Prenom LIKE %s OR Carte_RFID LIKE %s'
        cursor.execute(query, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
    else:
        cursor.execute('SELECT * FROM employe')
    
    users = cursor.fetchall()
    cursor.close()

    return render_template('all_users.html', users=users)

@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM employe WHERE ID_Employe = %s', (id,))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('all_users'))

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        carte_rfid = request.form.get('carte_rfid')
        cursor.execute('UPDATE employe SET Nom = %s, Prenom = %s, Carte_RFID = %s WHERE ID_Employe = %s',
                       (nom, prenom, carte_rfid, id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('all_users'))
    else:
        cursor.execute('SELECT * FROM employe WHERE ID_Employe = %s', (id,))
        user = cursor.fetchone()
        cursor.close()
        return render_template('edit_user.html', user=user)

@app.route('/check_rfid', methods=['POST'])
def check_rfid():
    data = request.get_json()
    uid = data.get('uid')

    if not uid:
        return jsonify({"status": "error", "message": "No UID provided"}), 400

    cursor = mysql.connection.cursor()
    try:
        # Vérifier si le RFID est autorisé
        cursor.execute('SELECT ID_Employe FROM employe WHERE Carte_RFID = %s', (uid,))
        result = cursor.fetchone()
        if result:
            id_employe = result[0]
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Vérifier s'il existe une entrée avec une Date_Sortie nulle
            cursor.execute('SELECT ID_Historique FROM historique WHERE ID_Employe = %s AND Date_Sortie IS NULL', (id_employe,))
            existing_entry = cursor.fetchone()

            if existing_entry:
                # Mettre à jour l'entrée existante avec l'heure actuelle comme Date_Sortie
                cursor.execute('UPDATE historique SET Date_Sortie = %s WHERE ID_Historique = %s', (current_time, existing_entry[0]))
            else:
                # Insérer une nouvelle entrée avec l'heure actuelle comme Date_Entree
                cursor.execute('INSERT INTO historique (ID_Employe, Date_Entree) VALUES (%s, %s)', (id_employe, current_time))
            
            mysql.connection.commit()

            return jsonify({"status": "authorized", "ID_Employe": id_employe})
        else:
            return jsonify({"status": "unauthorized"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()

@app.route('/log_rfid', methods=['POST'])
def log_rfid():
    return '"AUTORISER ET ENREGISTRER'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
