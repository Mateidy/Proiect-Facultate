from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
import threading
import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///senzori.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)


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
users = {"admin": generate_password_hash("admin")}
auto_mode = True

@app.route("/toggle_mode", methods=["POST"])
def toggle_mode():
    global auto_mode
    data = request.get_json()
    auto_mode = data.get("mode", True)
    return jsonify({"auto_mode": auto_mode})

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and check_password_hash(users[username], password):
            session["username"] = username
            return redirect(url_for("dashboard"))
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
    data = SensorData.query.order_by(SensorData.timestamp.desc()).limit(50).all()
    formatted_data = [
        {
            "timestamp": entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": entry.temperature,
            "humidity": entry.humidity,
            "light": entry.light
        }
        for entry in data
    ]
    return render_template("history.html", history_data=formatted_data)

@socketio.on('connect')
def on_connect():
    emit('update_data', sensor_data)

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
