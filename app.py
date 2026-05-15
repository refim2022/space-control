from flask import Flask, render_template, request, redirect, url_for, jsonify
import random
import threading
import time

app = Flask(__name__)

# логин/пароль
USERNAME = "Efimka"
PASSWORD = "17517"

# начальные телеметрические данные
telemetry = {
    "speed": 27000,       # км/ч
    "altitude": 450,      # км
    "temperature": -260,   # °C
    "battery": 100,    
    "time": 0    # %
}

# флаг для остановки потока при завершении сервера
running = True

# функция обновления телеметрии
def update_telemetry():
    while running:
        # скорость колеблется ±200 км/ч
        telemetry["speed"] += random.randint(-200, 200)
        # температура колеблется ±2 градуса, остаётся отрицательной
        telemetry["temperature"] += random.randint(-2, 2)
        if telemetry["temperature"] > -260:
            telemetry["temperature"] = -260
        # батарея снижается на 2% каждые 60 секунд
        #telemetry["battery"] -= 2
        #if telemetry["time"] == 60:
        #    telemetry["battery"] = max(0, telemetry["battery"] - 2)
        #telemetry["time"] == 0
        time.sleep(1)  # 60 секунд
        #telemetry["time"] += 1

# запускаем поток телеметрии
thread = threading.Thread(target=update_telemetry)
thread.daemon = True
thread.start()

# --------- Авторизация ---------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == USERNAME and password == PASSWORD:
            # батарея сбрасывается на 100 при входе
            telemetry["battery"] = 100
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Неверный логин или пароль")
    return render_template("login.html", error=None)

@app.route("/home")
def home():
    return render_template("index.html")

# --------- API ---------
@app.route("/telemetry")
def telemetry_route():
    return jsonify(telemetry)

@app.route("/capture")
def capture():
    return jsonify({"status": "Захват мусора запущен"})

@app.route("/return")
def return_base():
    return jsonify({"status": "Аппарат возвращается на базу"})

@app.route("/photo")
def photo():
    return jsonify({"status": "Фото сделано и отправлено на Землю"})

if __name__ == "__main__":
    try:
        app.run(debug=True)
    finally:
        running = False