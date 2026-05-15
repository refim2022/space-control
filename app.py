from flask import Flask, render_template, request, redirect, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_bcrypt import Bcrypt
import json
import random

app = Flask(__name__)
app.secret_key = "space-secret-key"

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ---------------- ПОЛЬЗОВАТЕЛЬ ----------------
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    return User(username)

# ---------------- БАЗА ПОЛЬЗОВАТЕЛЕЙ ----------------
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

# ---------------- СОСТОЯНИЕ СПУТНИКА ----------------
battery = 100
altitude = 400

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users and bcrypt.check_password_hash(users[username], password):
            login_user(User(username))
            return redirect("/")

        return "❌ Неверный логин или пароль"

    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users:
            return "Пользователь уже существует"

        hash_pass = bcrypt.generate_password_hash(password).decode("utf-8")
        users[username] = hash_pass
        save_users(users)

        return """
<h1 style='text-align:center;margin-top:150px;font-family:Arial'>
✅ Пользователь успешно создан!<br><br>
Спасибо за регистрацию 🚀<br><br>
<a href='/login'>Вернуться ко входу</a>
</h1>
"""

    return render_template("register.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

# ---------------- ГЛАВНАЯ ----------------
@app.route("/")
@login_required
def index():
    return render_template("index.html")

# ---------------- ТЕЛЕМЕТРИЯ (БЕЗ РАЗРЯДА) ----------------
@app.route("/telemetry")
@login_required
def telemetry():
    global battery, altitude

    data = {
        "speed": random.randint(26000, 28000),
        "altitude": altitude,
        "temperature": random.randint(-270, -260),
        "battery": battery
    }

    return jsonify(data)

# ---------------- АВАРИЙНЫЕ ДЕЙСТВИЯ ----------------
@app.route("/emergency/backup")
@login_required
def backup_battery():
    global battery
    battery = 50
    return jsonify({"status":"Запасная батарея активирована"})

@app.route("/emergency/shutdown")
@login_required
def shutdown():
    return jsonify({"status":"Система отключена"})

# ---------------- КОМАНДЫ СПУТНИКА ----------------
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

# ---------------- ЗАПУСК ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)