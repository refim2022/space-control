from flask import Flask, render_template, request, redirect, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.secret_key = "space-secret-key"

# БАЗА ДАННЫХ
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ---------- МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ ----------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------- СОЗДАНИЕ БАЗЫ ----------
@app.before_first_request
def create_tables():
    db.create_all()

# ---------- СОСТОЯНИЕ СПУТНИКА ----------
battery = 100
altitude = 400

# ---------- LOGIN ----------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()

        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect("/")

        return "❌ Неверный логин или пароль"

    return render_template("login.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

        if User.query.filter_by(username=username).first():
            return "Пользователь уже существует"

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return """
        <h1 style='text-align:center;margin-top:150px;font-family:Arial'>
        ✅ Пользователь создан!<br><br>
        Спасибо за внимание 🚀<br><br>
        <a href='/login'>Вернуться ко входу</a>
        </h1>
        """

    return render_template("register.html")

# ---------- LOGOUT ----------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

# ---------- ГЛАВНАЯ ----------
@app.route("/")
@login_required
def index():
    return render_template("index.html")

# ---------- ТЕЛЕМЕТРИЯ ----------
@app.route("/telemetry")
@login_required
def telemetry():
    data = {
        "speed": random.randint(26000, 28000),
        "altitude": altitude,
        "temperature": random.randint(-270, -260),
        "battery": battery
    }
    return jsonify(data)

# ---------- КОМАНДЫ ----------
@app.route("/capture")
@login_required
def capture():
    return jsonify({"status":"Мусор захвачен"})

@app.route("/return")
@login_required
def return_home():
    return jsonify({"status":"Возврат на базу"})

@app.route("/photo")
@login_required
def photo():
    return jsonify({"status":"Фото сделано"})

# ---------- ЗАПУСК ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)