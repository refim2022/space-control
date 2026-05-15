from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = "space-secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ------------------- DATABASE -------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20), default="operator")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ------------------- HOME -------------------

@app.route("/")
@login_required
def home():
    return render_template_string("""
        <h1>🚀 Space Control</h1>
        <p>Вы вошли как: <b>{{current_user.username}}</b></p>
        <p>Роль: <b>{{current_user.role}}</b></p>

        <a href="/logout">Выйти</a><br><br>

        {% if current_user.role == "admin" %}
            <a href="/admin">Админ панель</a>
        {% endif %}
    """)


# ------------------- REGISTER -------------------

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        if User.query.filter_by(username=username).first():
            return "Пользователь уже существует"

        # первый пользователь становится админом
        role = "admin" if User.query.count() == 0 else "operator"

        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        return render_template_string("""
            <h2>Регистрация завершена</h2>
            <p>Спасибо за внимание ❤️</p>
            <a href="/login">Вернуться ко входу</a>
        """)

    return render_template_string("""
        <h2>Регистрация</h2>
        <form method="post">
            Логин:<br><input name="username"><br><br>
            Пароль:<br><input name="password" type="password"><br><br>
            <button>Зарегистрироваться</button>
        </form>
        <br>
        <a href="/login">Назад</a>
    """)


# ------------------- LOGIN -------------------

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")

        return "Неверный логин или пароль"

    return render_template_string("""
        <h2>Вход</h2>
        <form method="post">
            Логин:<br><input name="username"><br><br>
            Пароль:<br><input name="password" type="password"><br><br>
            <button>Войти</button>
        </form>
        <br>
        <a href="/register">Регистрация</a>
    """)


# ------------------- LOGOUT -------------------

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


# ------------------- ADMIN PANEL -------------------

@app.route("/admin")
@login_required
def admin_panel():
    if current_user.role != "admin":
        return "Доступ запрещён"

    users = User.query.all()

    return render_template_string("""
        <h1>🛠 Админ панель</h1>
        <h3>Пользователи:</h3>

        {% for user in users %}
            <p>
                <b>{{user.username}}</b> — {{user.role}}

                {% if user.id != current_user.id %}
                    | <a href="/change_role/{{user.id}}">Сменить роль</a>
                    | <a href="/delete_user/{{user.id}}">Удалить</a>
                {% endif %}
            </p>
        {% endfor %}

        <br><a href="/">Назад</a>
    """, users=users)


# ------------------- CHANGE ROLE -------------------

@app.route("/change_role/<int:user_id>")
@login_required
def change_role(user_id):
    if current_user.role != "admin":
        return "Доступ запрещён"

    user = User.query.get(user_id)

    if user.id == current_user.id:
        return "Нельзя менять свою роль"

    user.role = "admin" if user.role == "operator" else "operator"
    db.session.commit()

    return redirect("/admin")


# ------------------- DELETE USER -------------------

@app.route("/delete_user/<int:user_id>")
@login_required
def delete_user(user_id):
    if current_user.role != "admin":
        return "Доступ запрещён"

    user = User.query.get(user_id)

    if user.id == current_user.id:
        return "Нельзя удалить самого себя"

    db.session.delete(user)
    db.session.commit()

    return redirect("/admin")


# ------------------- START -------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)