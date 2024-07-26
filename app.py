from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, set_access_cookies, \
    unset_jwt_cookies
import sqlite3
from fuzzywuzzy import fuzz
import re
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['JWT_SECRET_KEY'] = '20201998'  # Change this to a secure random key
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.secret_key = 'your_secret_key'  # For flash messages


# Database setup
def init_db():
    conn = sqlite3.connect('dictionary.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dictionary
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  word TEXT,
                  language TEXT,
                  meaning TEXT,
                  category TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT,
                  is_admin INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()


init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin/import_excel', methods=['GET', 'POST'])
@jwt_required()
def import_excel():
    current_user = get_jwt_identity()
    if not current_user['is_admin']:
        return jsonify({"msg": "Admins only!"}), 403

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                df = pd.read_excel(filepath)
                conn = sqlite3.connect('dictionary.db')
                cursor = conn.cursor()

                for _, row in df.iterrows():
                    word = row['word']
                    language = row['language']
                    meaning = row['meaning']
                    category = row['category']

                    # Insert the original word
                    cursor.execute('''
                        INSERT INTO dictionary (word, language, meaning, category)
                        VALUES (?, ?, ?, ?)
                    ''', (word, language, meaning, category))

                    # Insert the reverse association
                    reverse_language = 'Russian' if language == 'Turkish' else 'Turkish'
                    cursor.execute('''
                        INSERT INTO dictionary (word, language, meaning, category)
                        VALUES (?, ?, ?, ?)
                    ''', (meaning, reverse_language, word, category))

                conn.commit()
                conn.close()
                flash('File successfully imported with bidirectional associations')
            except Exception as e:
                flash(f'Error importing file: {str(e)}')

            os.remove(filepath)  # Remove the file after processing
            return redirect(url_for('admin_panel'))

    return render_template('import_excel.html')


@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    word = data.get('word', '')
    category = data.get('category', 'All')
    page = data.get('page', 1)
    per_page = 10

    conn = sqlite3.connect('dictionary.db')
    c = conn.cursor()

    query = '''SELECT word, language, meaning, category FROM dictionary 
               WHERE (word LIKE ? OR meaning LIKE ?) 
               AND (? = 'All' OR category = ?)'''
    c.execute(query, (f'%{word}%', f'%{word}%', category, category))

    all_results = c.fetchall()

    # Fuzzy matching
    fuzzy_results = []
    for result in all_results:
        if fuzz.partial_ratio(word.lower(), result[0].lower()) > 70 or fuzz.partial_ratio(word.lower(),
                                                                                          result[2].lower()) > 70:
            fuzzy_results.append(result)

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = fuzzy_results[start:end]

    results = [{'word': row[0], 'language': row[1], 'meaning': row[2], 'category': row[3]} for row in paginated_results]
    total_pages = (len(fuzzy_results) + per_page - 1) // per_page

    conn.close()

    return jsonify({'results': results, 'total_pages': total_pages})


# New route for adding words (admin only)
@app.route('/admin/add_word', methods=['POST'])
@jwt_required()
def admin_add_word():
    current_user = get_jwt_identity()
    if current_user != 'Mechres':  # Replace 'admin' with your actual admin username
        return jsonify({"msg": "Admins only!"}), 403
    data = request.get_json()
    word = data.get('word')
    language = data.get('language')
    meaning = data.get('meaning')
    category = data.get('category')

    if not all([word, language, meaning, category]):
        return jsonify({'error': 'All fields are required'}), 400

    if not re.match(r'^[a-zA-ZğüşıöçĞÜŞİÖÇ\s]+$', word):
        return jsonify({'error': 'Word should contain only letters and spaces'}), 400

    conn = sqlite3.connect('dictionary.db')
    c = conn.cursor()

    # Add the original word
    c.execute('INSERT INTO dictionary (word, language, meaning, category) VALUES (?, ?, ?, ?)',
              (word, language, meaning, category))

    # Add the reverse association
    reverse_language = 'Russian' if language == 'Turkish' else 'Turkish'
    c.execute('INSERT INTO dictionary (word, language, meaning, category) VALUES (?, ?, ?, ?)',
              (meaning, reverse_language, word, category))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Word added successfully in both languages'}), 201


@app.errorhandler(Exception)
def handle_error(e):
    print(f"An error occurred: {str(e)}")
    return jsonify(error=str(e)), 500


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        flash('Username and password are required', 'error')
        return redirect(url_for('index'))

    conn = sqlite3.connect('dictionary.db')
    c = conn.cursor()

    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        flash('User registered successfully', 'success')
    except sqlite3.IntegrityError:
        flash('Username already exists', 'error')
    finally:
        conn.close()

    return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('dictionary.db')
    c = conn.cursor()
    c.execute('SELECT password, is_admin FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user[0], password):
        access_token = create_access_token(identity={'username': username, 'is_admin': user[1]})
        response = jsonify({'login': True, 'is_admin': user[1]})
        set_access_cookies(response, access_token)
        flash('Logged in successfully', 'success')
        return response
    else:
        flash('Invalid username or password', 'error')
        return jsonify({'login': False}), 401


@app.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'logout': True})
    unset_jwt_cookies(response)
    flash('Logged out successfully', 'success')
    return response


@app.route('/admin')
@jwt_required()
def admin_panel():
    current_user = get_jwt_identity()
    if not current_user['is_admin']:
        return jsonify({"msg": "Admins only!"}), 403

    page = request.args.get('page', 1, type=int)
    per_page = 20

    conn = sqlite3.connect('dictionary.db')
    c = conn.cursor()

    # Fetch users with pagination
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    c.execute('SELECT id, username, is_admin FROM users LIMIT ? OFFSET ?', (per_page, (page - 1) * per_page))
    users = c.fetchall()

    # Fetch words with pagination
    c.execute('SELECT COUNT(*) FROM dictionary')
    total_words = c.fetchone()[0]
    c.execute('SELECT id, word, language, meaning, category FROM dictionary LIMIT ? OFFSET ?',
              (per_page, (page - 1) * per_page))
    words = c.fetchall()

    conn.close()

    return render_template('admin.html',
                           users=users,
                           words=words,
                           page=page,
                           per_page=per_page,
                           total_users=total_users,
                           total_words=total_words)


@app.route('/admin/edit_word', methods=['POST'])
@jwt_required()
def admin_edit_word():
    current_user = get_jwt_identity()
    if not current_user['is_admin']:
        return jsonify({"msg": "Admins only!"}), 403

    data = request.get_json()
    word_id = data.get('id')
    word = data.get('word')
    language = data.get('language')
    meaning = data.get('meaning')
    category = data.get('category')

    if not all([word_id, word, language, meaning, category]):
        return jsonify({'error': 'All fields are required'}), 400

    if not re.match(r'^[a-zA-ZğüşıöçĞÜŞİÖÇ\s]+$', word):
        return jsonify({'error': 'Word should contain only letters (including Turkish characters) and spaces'}), 400

    conn = sqlite3.connect('dictionary.db')
    c = conn.cursor()

    c.execute('UPDATE dictionary SET word=?, language=?, meaning=?, category=? WHERE id=?',
              (word, language, meaning, category, word_id))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Word updated successfully'}), 200


@app.route('/admin/delete_word', methods=['POST'])
@jwt_required()
def admin_delete_word():
    current_user = get_jwt_identity()
    if not current_user['is_admin']:
        return jsonify({"msg": "Admins only!"}), 403

    data = request.get_json()
    word_id = data.get('id')

    if not word_id:
        return jsonify({'error': 'Word ID is required'}), 400

    conn = sqlite3.connect('dictionary.db')
    c = conn.cursor()

    c.execute('DELETE FROM dictionary WHERE id=?', (word_id,))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Word deleted successfully'}), 200


@app.route('/admin/manage_user', methods=['POST'])
@jwt_required()
def admin_manage_user():
    current_user = get_jwt_identity()
    if not current_user['is_admin']:
        return jsonify({"msg": "Admins only!"}), 403

    data = request.get_json()
    user_id = data.get('id')
    action = data.get('action')  # 'delete' or 'toggle_admin'

    if not user_id or not action:
        return jsonify({'error': 'User ID and action are required'}), 400

    conn = sqlite3.connect('dictionary.db')
    c = conn.cursor()

    if action == 'delete':
        c.execute('DELETE FROM users WHERE id=?', (user_id,))
    elif action == 'toggle_admin':
        c.execute('UPDATE users SET is_admin = 1 - is_admin WHERE id=?', (user_id,))
    else:
        conn.close()
        return jsonify({'error': 'Invalid action'}), 400

    conn.commit()
    conn.close()

    return jsonify({'message': f'User {action} successful'}), 200


@app.route('/register_admin', methods=['POST'])
def register_admin():
    username = request.form['username']
    password = request.form['password']
    admin_key = request.form['admin_key']  # A secret key to allow admin registration

    if not username or not password:
        flash('Username and password are required', 'error')
        return redirect(url_for('index'))

    if admin_key != 'your_secret_admin_key':  # Replace with a secure key
        flash('Invalid admin key', 'error')
        return redirect(url_for('index'))

    conn = sqlite3.connect('dictionary.db')
    c = conn.cursor()

    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        c.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                  (username, hashed_password, 1))
        conn.commit()
        flash('Admin user registered successfully', 'success')
    except sqlite3.IntegrityError:
        flash('Username already exists', 'error')
    finally:
        conn.close()

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
