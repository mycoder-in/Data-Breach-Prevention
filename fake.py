import os
from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder if not exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        return redirect(url_for("index"))
    
    
    

@app.route("/admin/view/<filename>")
def view_file(filename):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return f"<h3>Viewing {filename}</h3><pre>{content}</pre><a href='/admin'>⬅️ Back</a>"
    except:
        return "❌ Cannot display this file (maybe it's not text)."

@app.route("/admin/download/<filename>")
def download_file(filename):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    return send_file(filepath, as_attachment=True)

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder if not exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        return redirect(url_for("index"))
    
    return '''
        <h2>Upload File</h2>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <input type="submit" value="Upload">
        </form>
        <br>
       
    '''

@app.route("/admin")
def admin_panel():
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    links = [f"<li><a href='/admin/view/{f}'>{f}</a> | <a href='/admin/download/{f}'>Download</a></li>" for f in files]
    return f'''
        <a href="/">⬅️ Back to Upload</a>
    '''

@app.route("/admin/view/<filename>")
def view_file(filename):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return f"<h3>Viewing {filename}</h3><pre>{content}</pre><a href='/admin'>⬅️ Back</a>"
    except:
        return "❌ Cannot display this file (maybe it's not text)."

@app.route("/admin/download/<filename>")
def download_file(filename):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
