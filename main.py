from flask import Flask,request,flash,redirect
from flask.helpers import url_for
from flask.json.tag import TaggedJSONSerializer
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_manager, login_user,LoginManager,login_required,current_user,logout_user
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy.orm import relationship
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://wfnlfhyareftoi:7e0023d6c43dd51d32b1f4c55d6c56e4d4cfc62af2422aa4c02c28d9e281d9a9@ec2-54-158-232-223.compute-1.amazonaws.com:5432/devndig2l8l9aj'
app.config['SECRET_KEY'] = "142353453457463421341"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model , UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(1200), unique=True, nullable=False)
    password = db.Column(db.String(120),nullable=False)
    name = db.Column(db.String(120),nullable=False)
    tsk = relationship("Task", backref="author")


class Task(db.Model):
    __tablename__ = "tasks" 
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(8000) , nullable=False)
    tsk_dt = db.Column(db.DateTime , nullable=False,
        default=datetime.now)
    author_id = db.Column(db.Integer,db.ForeignKey("users.id"))

  
db.create_all()

@app.route("/" , methods=["GET" , "POST"])
def home():
    if request.method == "POST":
        tsk = request.form.get("tsk")
        new_tsk = Task(
            task = tsk,
            author = current_user,
        )
        db.session.add(new_tsk)
        db.session.commit()
    return render_template("index.html" ,current_user = current_user)

@app.route("/signup", methods=["GET" , "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        if User.query.filter_by(email = email).first():
            flash ("The user already exists: Please Login")
            return redirect(url_for("login"))
        else:
            new_user = User(
                email = email,
                password = generate_password_hash(password, salt_length=8),
                name = name,
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("home"))
    return render_template("signup.html")

@app.route("/login", methods=['GET' , 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email = email).first()
        if not user:
            flash("User does't Exists")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password , password):
            flash("Password incorrect")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/done")
def done():
    tsk_id = request.args.get("id")
    done_tsk = Task.query.get(tsk_id)
    db.session.delete(done_tsk)
    db.session.commit()
    return redirect(url_for("home"))
        
   
















if __name__ == "__main__":
    app.run(debug=False)