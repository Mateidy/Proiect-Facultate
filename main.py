from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
import threading
import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'
socketio = SocketIO(app)

sensor_data = {
    'temperature': None,
    'humidity': None,
    'light': None,
    'timestamp': None
}

sensor_data_lock = threading.Lock()
users = {"admin": generate_password_hash("admin")}

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

@app.route("/sensor_data", methods=["POST"])
def receive_sensor_data():
    global sensor_data
    data = request.get_json()
    if data and 'sensor' in data and 'value' in data:
        sensor = data['sensor']
        value = data['value']
        with sensor_data_lock:
            sensor_data[sensor] = value

            if all(sensor_data[sensor] is not None for sensor in ['temperature', 'humidity', 'light']):
                sensor_data['timestamp'] = datetime.datetime.now().strftime("%H:%M:%S")
                socketio.emit('update_data', sensor_data)

                for key in ['temperature', 'humidity', 'light']:
                    sensor_data[key] = None
                sensor_data['timestamp'] = None
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Invalid data"}), 400

@socketio.on('connect')
def on_connect():
    emit('update_data', sensor_data)

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
