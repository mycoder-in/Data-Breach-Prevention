import os
from flask import Flask, request, render_template_string, send_file, redirect, url_for, session
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'csv', 'json', 'db'}

# Generate or load encryption key
KEY_FILE = "secret.key"
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
else:
    with open(KEY_FILE, "rb") as f:
        key = f.read()

fernet = Fernet(key)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# --- Login Page ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        if user == 'admin' and pwd == '12345':
            session['user'] = user
            return redirect(url_for('admin_panel'))
        elif user == 'user' and pwd == 'userpass':
            session['user'] = user
            return redirect(url_for('user_panel'))
        return 'Invalid credentials'
    return '''
        <h2>Login</h2>
        <form method="post">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

# --- File Upload (Admin only) ---
@app.route('/upload', methods=['GET', 'POST']) 
def upload():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], filename + '.enc')
            encrypted_data = fernet.encrypt(file.read())
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            return '✅ File uploaded and encrypted'
    return '''
        <h2>Upload File (Admin)</h2>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file"><br>
            <input type="submit" value="Upload">
        </form>
        <a href="/admin">Go to Admin Panel</a>
    '''

# --- Admin Panel to Manage Files ---
@app.route('/admin')
def admin_panel():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.enc')]
    file_links = ''.join(
        f"<li>{f} | "
        f"<a href='/admin/view_encrypted/{f}'>🔒 Encrypted Message</a> | "
        f"<a href='/download/{f}'>📥 Download</a></li>"
        for f in files
    )
    return f'''
        <h2>👨‍💻 Fake Admin Panel</h2>
        <ul>{file_links}</ul>
        <a href="/upload">⬆️ Upload New File</a><br>
        <a href="/logout">Logout</a>
    '''

# --- View Raw Encrypted Message ---
@app.route('/admin/view_encrypted/<filename>')
def view_encrypted(filename):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(filepath):
        return "❌ File not found"
    with open(filepath, "rb") as f:
        data = f.read()
    return render_template_string(f'''
        <h2>🔐 Encrypted Content: {filename}</h2>
        <textarea style="width: 100%; height: 300px;">{data.decode()}</textarea>
        <br><a href="/admin">⬅️ Back</a>
    ''')

# --- Download Decrypted File (Admin/User) ---
@app.route('/download/<filename>')
def download_file(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return '❌ File not found'
    encrypted = open(file_path, 'rb').read()
    decrypted = fernet.decrypt(encrypted)
    decrypted_path = os.path.join(UPLOAD_FOLDER, 'decrypted_' + filename.replace('.enc', ''))
    with open(decrypted_path, 'wb') as f:
        f.write(decrypted)
    return send_file(decrypted_path, as_attachment=True)

# --- User Panel to List Files ---
@app.route('/user_panel')
def user_panel():
    if 'user' not in session or session['user'] != 'user':
        return redirect(url_for('login'))
    files = [f.replace('.enc', '') for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.enc')]
    file_list = ''.join(f"<li>{f} <a href='/download/{f}.enc'>📥 Download</a></li>" for f in files)
    return f'''
        <h2>User Panel</h2>
        <ul>{file_list}</ul>
        <a href="/logout">Logout</a>
    '''

# --- Logout ---
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
