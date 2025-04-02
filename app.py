from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'json', 'db'}

# Generate or load an encryption key
KEY_FILE = "secret.key"
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
else:
    with open(KEY_FILE, "rb") as key_file:
        key = key_file.read()

encryption = Fernet(key)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':  # Simple authentication
            session['user'] = username
            return redirect(url_for('upload'))
        elif username == 'user' and password == 'userpass':  # User panel access
            session['user'] = username
            return redirect(url_for('user_panel'))
        return 'Invalid credentials, try again.'
    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            return 'No file selected'
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename + ".enc")
            file_data = file.read()
            encrypted_data = encryption.encrypt(file_data)
            with open(file_path, "wb") as enc_file:
                enc_file.write(encrypted_data)
            return 'File encrypted and uploaded successfully'
        return 'Invalid file type'
    return render_template('upload.html')

@app.route('/user_panel')
def user_panel():
    if 'user' not in session or session['user'] != 'user':
        return redirect(url_for('login'))
    files = [f.replace(".enc", "") for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".enc")]
    return render_template('user_panel.html', files=files)

@app.route('/download/<filename>')
def download(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename + ".enc")
    if not os.path.exists(file_path):
        return 'File not found'
    
    with open(file_path, "rb") as enc_file:
        encrypted_data = enc_file.read()
        decrypted_data = encryption.decrypt(encrypted_data)
    
    decrypted_file_path = os.path.join(app.config['UPLOAD_FOLDER'], "decrypted_" + filename)
    with open(decrypted_file_path, "wb") as dec_file:
        dec_file.write(decrypted_data)
    
    return send_file(decrypted_file_path, as_attachment=True)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
