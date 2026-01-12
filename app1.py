from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_file
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from config import SECRET_KEY, POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT
import pandas as pd
import io
import logging

from datetime import datetime

app = Flask(__name__)

# Activer CORS pour permettre les requêtes depuis les appareils RFID
CORS(app)

# Configuration du logging en mode debug
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Clé secrète pour sécuriser les sessions
app.secret_key = SECRET_KEY

# Fonction pour obtenir une connexion PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB,
        port=POSTGRES_PORT
    )

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error_msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:
            if username == 'ADMIN' and password == 'ADMIN':
                session['loggedin'] = True
                session['id'] = 1
                session['username'] = 'ADMIN'
                return redirect(url_for('ADMIN'))

            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                cursor.execute('SELECT * FROM userinterface WHERE username = %s', (username,))
                user = cursor.fetchone()
                if user and user['password'] == password and user['approve'] == True:
                    session['loggedin'] = True
                    session['id'] = user['id_user']
                    session['username'] = user['username']
                    return redirect(url_for('dashboard'))
                else:
                    error_msg = 'Nom d\'utilisateur ou mot de passe incorrect!'
            except Exception as e:
                error_msg = 'Une erreur s\'est produite lors de la tentative de connexion.'
                print(f"Database error: {e}")
            finally:
                cursor.close()
                conn.close()
        else:
            error_msg = 'Veuillez fournir un nom d\'utilisateur et un mot de passe.'

    return render_template('login.html', error_msg=error_msg)

@app.route('/ADMIN')
def ADMIN():
    if 'loggedin' in session and session['username'] == 'ADMIN':
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute('SELECT * FROM userinterface WHERE approve = false')
            user_requests = cursor.fetchall()
            return render_template('admin.html', user_requests=user_requests)
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('login'))




@app.route('/approve_user/<int:user_id>', methods=['GET'])
def approve_user(user_id):
    if 'loggedin' in session and session['username'] == 'ADMIN':
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute('UPDATE userinterface SET approve = true WHERE id_user = %s', (user_id,))
            conn.commit()
            return redirect(url_for('ADMIN'))
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('login'))

@app.route('/reject_user/<int:user_id>', methods=['GET'])
def reject_user(user_id):
    if 'loggedin' in session and session['username'] == 'ADMIN':
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute('DELETE FROM userinterface WHERE id_user = %s', (user_id,))
            conn.commit()
            return redirect(url_for('ADMIN'))
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()
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

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO userinterface (username, password, approve) VALUES (%s, %s, %s)', (username, password, False))
        conn.commit()
        cursor.close()
        conn.close()

        return 'Inscription réussie!'

    return render_template('register.html')
@app.route('/logout')
def logout():
    # Supprimer toutes les variables de session
    session.clear()
    # Rediriger vers la page de connexion
    return redirect(url_for('login'))




@app.route('/view_history', methods=['GET', 'POST'])
def view_history():
    if request.method == 'POST':
        name = request.form.get('name')
        date_start = request.form.get('date_start')
        date_end = request.form.get('date_end')

        params = {'name': f"%{name}%" if name else None, 'date_start': date_start, 'date_end': date_end}

        conn = get_db_connection()
        cur = conn.cursor()
        # Adaptation de la requête pour PostgreSQL
        query = """
            SELECT employe.nom, employe.prenom, historique.date_entree, historique.date_sortie
            FROM historique
            INNER JOIN employe ON historique.id_employe = employe.id_employe
            WHERE (%(name)s IS NULL OR employe.nom LIKE %(name)s)
            AND (%(date_start)s IS NULL OR (historique.date_entree >= %(date_start)s AND historique.date_sortie <= %(date_end)s))
        """
        cur.execute(query, params)
        data = cur.fetchall()
        cur.close()
        conn.close()

        if request.form.get('export') == 'true':
            if data:
                output = io.BytesIO()
                df = pd.DataFrame(data, columns=['Nom', 'Prénom', 'Date d\'Entrée', 'Date de Sortie'])
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Historique')
                output.seek(0)
                return send_file(output, as_attachment=True, attachment_filename='historique_employes.xlsx')
            else:
                return "Aucune donnée à exporter."

    return render_template('view_history.html', history=data if 'data' in locals() else None)

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
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO employe (nom, prenom, carte_rfid) VALUES (%s, %s, %s)', (nom, prenom, carte_rfid))
                conn.commit()
                success_msg = 'Employé ajouté avec succès!'
            except Exception as e:
                error_msg = 'Une erreur s\'est produite lors de l\'ajout de l\'employé.'
                print(f"Database error: {e}")
            finally:
                cursor.close()
                conn.close()
        else:
            error_msg = 'Veuillez remplir tous les champs.'

    return render_template('add_employee.html', error_msg=error_msg, success_msg=success_msg)

@app.route('/all_users', methods=['GET', 'POST'])
def all_users():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        if request.method == 'POST':
            search_query = request.form.get('search_query', '')
            # Sanitize input to prevent SQL injection
            search_query = '%' + search_query + '%'
            query = 'SELECT * FROM employe WHERE nom LIKE %s OR prenom LIKE %s OR carte_rfid LIKE %s'
            cursor.execute(query, (search_query, search_query, search_query))
        else:
            cursor.execute('SELECT * FROM employe')
        
        users = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('all_users.html', users=users)
    except Exception as e:
        # Handle exceptions gracefully
        cursor.close()
        conn.close()
        return "An error occurred: " + str(e)
@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM employe WHERE id_employe = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('all_users'))

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        carte_rfid = request.form.get('carte_rfid')
        cursor.execute('UPDATE employe SET nom = %s, prenom = %s, carte_rfid = %s WHERE id_employe = %s',
                       (nom, prenom, carte_rfid, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('all_users'))
    else:
        cursor.execute('SELECT * FROM employe WHERE id_employe = %s', (id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit_user.html', user=user)

@app.route('/check_rfid', methods=['POST', 'GET', 'OPTIONS'])
def check_rfid():
    try:
        # Log de la requête reçue
        logger.info(f"Requête reçue - Method: {request.method}, Headers: {dict(request.headers)}")
        
        # Gérer les requêtes OPTIONS pour CORS
        if request.method == 'OPTIONS':
            return jsonify({"status": "ok"}), 200
        
        # Récupérer les données (JSON ou form-data)
        if request.is_json:
            data = request.get_json()
            uid = data.get('uid') if data else None
        else:
            # Si ce n'est pas du JSON, essayer form-data
            uid = request.form.get('uid') or request.args.get('uid')
        
        # Si toujours pas de UID, essayer de le récupérer du body brut
        if not uid:
            try:
                raw_data = request.get_data(as_text=True)
                logger.info(f"Données brutes reçues: {raw_data}")
                # Essayer de parser comme JSON
                import json
                data = json.loads(raw_data) if raw_data else {}
                uid = data.get('uid')
            except:
                pass
        
        logger.info(f"UID extrait (brut): {uid}")
        
        if not uid:
            logger.warning("Aucun UID fourni dans la requête")
            return jsonify({"status": "error", "message": "No UID provided"}), 400
        
        # Nettoyer le UID (enlever les espaces, convertir en string, normaliser)
        uid_original = str(uid).strip()
        # Normaliser l'UID : enlever les espaces et convertir en majuscules
        uid_clean = uid_original.replace(" ", "").replace("-", "").upper()
        # Créer le format avec espaces (ex: "02 4A E4 F1")
        if len(uid_clean) >= 2:
            uid_with_spaces = " ".join([uid_clean[i:i+2] for i in range(0, len(uid_clean), 2)])
        else:
            uid_with_spaces = uid_clean
        
        logger.info(f"UID original: {uid_original}")
        logger.info(f"UID nettoyé (sans espaces): {uid_clean}")
        logger.info(f"UID formaté (avec espaces): {uid_with_spaces}")
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            # Check if the RFID is authorized
            # Rechercher avec tous les formats possibles (avec et sans espaces, majuscules/minuscules)
            logger.info(f"Recherche de la carte RFID avec formats: original={uid_original}, clean={uid_clean}, with_spaces={uid_with_spaces}")
            
            # Rechercher avec tous les formats possibles
            cursor.execute('''
                SELECT id_employe, nom, prenom 
                FROM employe 
                WHERE UPPER(REPLACE(REPLACE(carte_rfid, ' ', ''), '-', '')) = %s
                   OR UPPER(TRIM(carte_rfid)) = %s
                   OR UPPER(carte_rfid) = %s
                   OR carte_rfid = %s
                   OR carte_rfid = %s
                   OR carte_rfid = %s
            ''', (uid_clean, uid_clean, uid_with_spaces, uid_original, uid_clean, uid_with_spaces))
            result = cursor.fetchone()
            
            if result:
                id_employe = result['id_employe']
                nom = result['nom']
                prenom = result['prenom']
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                logger.info(f"Carte autorisée - Employé ID: {id_employe}, Nom: {nom} {prenom}")
                
                # Check for an existing entry with a null date_sortie
                cursor.execute('SELECT id_historique FROM historique WHERE id_employe = %s AND date_sortie IS NULL', (id_employe,))
                existing_entry = cursor.fetchone()

                if existing_entry:
                    # Update the existing entry with the current time as date_sortie
                    cursor.execute('UPDATE historique SET date_sortie = %s WHERE id_historique = %s', (current_time, existing_entry['id_historique']))
                    logger.info(f"Sortie enregistrée pour l'employé ID: {id_employe}")
                    message = "Sortie enregistrée"
                else:
                    # Insert a new entry with the current time as date_entree
                    cursor.execute('INSERT INTO historique (id_employe, date_entree) VALUES (%s, %s)', (id_employe, current_time))
                    logger.info(f"Entrée enregistrée pour l'employé ID: {id_employe}")
                    message = "Entrée enregistrée"
                
                conn.commit()

                return jsonify({
                    "status": "authorized",
                    "id_employe": id_employe,
                    "nom": nom,
                    "prenom": prenom,
                    "message": message,
                    "timestamp": current_time
                }), 200
            else:
                logger.warning(f"Carte non autorisée - UID: {uid}")
                return jsonify({
                    "status": "unauthorized",
                    "message": "Carte RFID non reconnue"
                }), 401
        except psycopg2.Error as e:
            logger.error(f"Erreur PostgreSQL: {str(e)}")
            conn.rollback()
            return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
        except Exception as e:
            logger.error(f"Erreur générale: {str(e)}")
            if conn:
                conn.rollback()
            return jsonify({"status": "error", "message": f"Error: {str(e)}"}), 500
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        logger.error(f"Erreur dans check_rfid: {str(e)}")
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

@app.route('/log_rfid', methods=['POST', 'GET'])
def log_rfid():
    """Route pour logging RFID - appelée après check_rfid si autorisé"""
    try:
        logger.info("Route /log_rfid appelée")
        # Récupérer les données
        if request.is_json:
            data = request.get_json()
            uid = data.get('uid') if data else None
            id_employe = data.get('ID_Employe') if data else None
        else:
            uid = request.form.get('uid') or request.args.get('uid')
            id_employe = request.form.get('ID_Employe') or request.args.get('ID_Employe')
        
        if uid:
            logger.info(f"Log RFID confirmé - UID: {uid}, ID_Employe: {id_employe}")
            # Le traitement a déjà été fait dans check_rfid, on confirme juste
            return jsonify({
                "status": "ok", 
                "message": "AUTORISER ET ENREGISTRER",
                "uid": uid,
                "id_employe": id_employe
            }), 200
        else:
            logger.warning("Route /log_rfid appelée sans UID")
            return jsonify({"status": "ok", "message": "AUTORISER ET ENREGISTRER"}), 200
    except Exception as e:
        logger.error(f"Erreur dans log_rfid: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("Démarrage de l'application Flask en mode DEBUG")
    logger.info("=" * 50)
    logger.info(f"Host: 0.0.0.0")
    logger.info(f"Port: 5000")
    logger.info(f"Debug: True")
    logger.info(f"Base de données: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
    logger.info("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)
