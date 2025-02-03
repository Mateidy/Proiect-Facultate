from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import threading
import datetime

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

FLASK_API_URL = os.getenv("FLASK_API_URL")

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    light = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<SensorData {self.timestamp} - Temp: {self.temperature}, Hum: {self.humidity}, Light: {self.light}>'


with app.app_context():
    db.create_all()


sensor_data = {'temperature': None, 'humidity': None, 'light': None, 'timestamp': None}
sensor_data_lock = threading.Lock()
username = os.getenv("USERNAME")
password_hash = os.getenv("PASSWORD_HASH")
auto_mode = True

@app.route("/toggle_mode", methods=["POST"])
def toggle_mode():
    global auto_mode
    data = request.get_json()
    auto_mode = data.get("mode", True)


    socketio.emit('mode_change', {"auto_mode": auto_mode})

    return jsonify({"auto_mode": auto_mode})

@app.route("/get_mode", methods=["GET"])
def get_mode():
    return jsonify({"auto_mode": auto_mode})



@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        entered_username = request.form["username"]
        entered_password = request.form["password"]

        if entered_username == username and check_password_hash(password_hash, entered_password):
            session["username"] = entered_username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials", 401

    return render_template("login.html")



@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

def delete_old_data():
    with app.app_context():
        count = SensorData.query.count()
        if count > 50:
            oldest_entry = SensorData.query.order_by(SensorData.timestamp.asc()).first()
            db.session.delete(oldest_entry)
            db.session.commit()

@app.route("/sensor_data", methods=["POST"])
def receive_sensor_data():
    global sensor_data
    if not auto_mode:
        return jsonify({"status": "error", "message": "Mod Manual - Datele nu sunt salvate"}), 400

    data = request.get_json()
    if data and 'sensor' in data and 'value' in data:
        sensor = data['sensor']
        value = data['value']
        with sensor_data_lock:
            sensor_data[sensor] = value
            if all(sensor_data[sensor] is not None for sensor in ['temperature', 'humidity', 'light']):
                new_entry = SensorData(temperature=sensor_data['temperature'], humidity=sensor_data['humidity'], light=sensor_data['light'])
                db.session.add(new_entry)
                db.session.commit()
                delete_old_data()
                sensor_data['timestamp'] = datetime.datetime.now().strftime("%H:%M:%S")
                socketio.emit('update_data', sensor_data)
                for key in ['temperature', 'humidity', 'light']:
                    sensor_data[key] = None
                sensor_data['timestamp'] = None
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Invalid data"}), 400


@app.route("/history")
def history():
    data = SensorData.query.order_by(SensorData.timestamp.desc()).limit(50).all()  # Luăm ultimele 70 de înregistrări

    grouped_data = [data[i:i+5] for i in range(0, len(data), 5)]

    medii_temperatura = []
    medii_umiditate = []
    medii_lumina = []

    for group in grouped_data[:7]:
        if len(group) == 5:
            avg_temp = round(sum(entry.temperature for entry in group) / 5, 2)
            avg_humidity = round(sum(entry.humidity for entry in group) / 5, 2)
            avg_light = round(sum(entry.light for entry in group) / 5, 2)
        else:
            avg_temp, avg_humidity, avg_light = "N/A", "N/A", "N/A"

        medii_temperatura.append(avg_temp)
        medii_umiditate.append(avg_humidity)
        medii_lumina.append(avg_light)

    if data:
        medie_temp_totala = round(sum(entry.temperature for entry in data) / len(data), 2)
        medie_umiditate_totala = round(sum(entry.humidity for entry in data) / len(data), 2)
        medie_lumina_totala = round(sum(entry.light for entry in data) / len(data), 2)
    else:
        medie_temp_totala, medie_umiditate_totala, medie_lumina_totala = "N/A", "N/A", "N/A"

    medii_temperatura.append(medie_temp_totala)
    medii_umiditate.append(medie_umiditate_totala)
    medii_lumina.append(medie_lumina_totala)

    formatted_data = [
        {
            "timestamp": entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": entry.temperature,
            "humidity": entry.humidity,
            "light": entry.light
        }
        for entry in data
    ]

    return render_template("history.html",
                           history_data=formatted_data,
                           medii_temperatura=medii_temperatura,
                           medii_umiditate=medii_umiditate,
                           medii_lumina=medii_lumina)



@socketio.on('connect')
def on_connect():
    emit('update_data', sensor_data)

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)