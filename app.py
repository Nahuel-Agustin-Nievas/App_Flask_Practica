from io import BytesIO

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import io

import os


# configuration of a context path for database

# UPLOAD_FOLDER = os.path.abspath("./uploads/")  probar en caso de que la ruta de abajo falle

f = os.path.abspath('app.py')
 
BASE_DIR = os.path.dirname(f)
DB_FILE = os.path.join(BASE_DIR, "database", "blog.db")
DB_URI = "sqlite:///" + DB_FILE
SECRET_KEY = "1234"
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = set(["pdf", "doc", "docx", "txt"])


# the next function check the files extension

def allowed_files(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = SECRET_KEY
db = SQLAlchemy(app)


# the next line helps with the RuntimeError: Working Outside of Application Context
app.app_context().push()
       

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    text = db.Column(db.String, nullable=False)

class PostFile(db.Model):
    __tablename__ = "post_files"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    filename = db.Column(db.String(50), nullable=True)
    data = db.Column(db.LargeBinary, nullable=True)
    download_url = db.Column(db.String(200), nullable=True)
    file_type = db.Column(db.String(10), nullable=True)



@app.route('/') 
def index():
    posts = Post.query.order_by(Post.date.desc()).all()
    post_files = PostFile.query.all()
    return render_template("index.html", posts=posts, post_files=post_files)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='sha256')
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return redirect('/login')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            # Iniciar sesión del usuario aquí
            # Redirigir al usuario a la página principal o a una página protegida
            return redirect('/')
        else:
            #     Mostrar un mensaje de error al usuario
            return "Usuario o contraseña incorrecta"
    return render_template('login.html')



@app.route('/add')   
def add():
    return render_template("add.html") 



@app.route('/create', methods=['GET','POST'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('titulo')
        text = request.form.get('texto')
        # print(request.files)
        files = request.files.getlist("ourfile[]")
        post = Post(title=title, text=text)
        db.session.add(post)
        db.session.flush()  # flush to get the post's ID
        if files and files[0].filename != '':
            for f in files: # iterate over the uploaded files
                if f.filename.endswith(".pdf") or f.filename.endswith(".txt") or f.filename.endswith(".doc") or f.filename.endswith(".jpg") or f.filename.endswith(".png"):
                    if f.filename.endswith(".jpg") or f.filename.endswith(".png") or f.filename.endswith(".jpeg"):
                        # Open image and resize while maintaining aspect ratio
                        image = Image.open(f)
                        file_type = image.format
                        image.thumbnail((1920, 1080))
                        # convert image to bytes
                        img_bytes = io.BytesIO()
                        image.save(img_bytes, format=image.format)
                        img_bytes = img_bytes.getvalue()
                        # generate a unique download URL for the file
                        download_url = f"/download2/{post.id}/{f.filename}"
                        post_file = PostFile(post_id=post.id, filename=f.filename, data=img_bytes, download_url=download_url, file_type=file_type)
                        db.session.add(post_file)
                    else:
                        # generate a unique download URL for the file
                        download_url = f"/download2/{post.id}/{f.filename}"
                        post_file = PostFile(post_id=post.id, filename=f.filename, data=f.read(), download_url=download_url)
                        db.session.add(post_file)
                else:
                    return "Solo se permiten archivos pdf, txt, doc, jpg o png."
        db.session.commit()
        
    return redirect('/')






@app.route('/delete', methods=['POST'])
def delete():
    post_id = request.form.get('post_id')
    post = db.session.query(Post).filter(Post.id == post_id).first()
    db.session.delete(post)
    post_files= db.session.query(PostFile).filter(PostFile.post_id == post_id).all()
    for post_file in post_files:
        db.session.delete(post_file) 
    db.session.commit()
    return redirect('/')


# @app.route('/upload', methods=['GET','POST'])
# def upload():
#     if request.method == 'POST':
#         if "ourfile" not in request.files:
#             return "The form has no file part."
#         f = request.files["ourfile"]
#         if f.filename == "":
#             return "No File Selected."  
#         if f and allowed_files(f.filename):
#             filename = secure_filename(f.filename)
#             f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
#             return redirect(url_for("get_file", filename=filename))
#         return "File not allowed"

@app.route('/download',  methods=['POST'])
def download():
    post_id = request.form.get('post_download_id')
    return redirect('/download2/' + post_id)
    


#  ruta download2 original ---------------------
# @app.route('/download2/<upload_id>')
# def download2(upload_id):

    
#     # post = Post.query.filter_by(id=upload_id).first()
#     # post = db.session.query(Post).filter(Post.id == upload_id).first()
#     # return send_file(BytesIO(post.data), attachment_filename=post.filename, as_attachment= True)
#     upload = Post.query.filter_by(id=upload_id).first()
#     if upload.data:
#         return send_file(BytesIO(upload.data), as_attachment=True, download_name=upload.filename)

#     return  "No file uploaded"

# ---------------------------------------------------------------------------


@app.route('/download2/<upload_id>/<filename>', methods=['POST'])
def download_file(upload_id, filename):
    post_file = PostFile.query.filter_by(post_id=upload_id, filename=filename).first()
    if not post_file:
        return "File not found"
    return send_file(BytesIO(post_file.data), as_attachment=True, download_name=post_file.filename)
    
    


# @app.before_first_request
# def create_tables():
#     db.create_all()



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port = 7060) 