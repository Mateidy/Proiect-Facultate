from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

def get_latest_sensor_data():
    conn = sqlite3.connect("senzori.db")
    cursor = conn.cursor()

    cursor.execute("SELECT temperature, humidity, light FROM SensorData ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()

    conn.close()

    if row:
        return {"temperature": row[0], "humidity": row[1], "light": row[2]}
    else:
        return None
@app.route("/")
def home():
    return jsonify({"message": "Flask API is running! Use /get_sensor_data to fetch sensor data."})


@app.route("/get_sensor_data", methods=["GET"])
def get_sensor_data():
    latest_data = get_latest_sensor_data()
    if latest_data:
        return jsonify(latest_data)
    else:
        return jsonify({"error": "No data available"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5001)
