from flask import Flask , render_template
from flask_socketio import SocketIO , emit
import random
import threading
from time import sleep


app=Flask(__name__)
socketio=SocketIO(app)

temperature=None
humidity=None
light=None


def get_temperature():
    return round (random.uniform(15,45),2)

def get_humidity():
    return round (random.uniform(20,90),2)

def get_light():
    return round(random.uniform(0,100),2)

def update_sensor_data():
    global temperature,humidity,light
    while True:
        temperature=get_temperature()
        humidity=get_humidity()
        light=get_light()
        socketio.emit('update_data',{
            'temperature':temperature,
            'humidity':humidity,
            'light':light,
        }
        )
        sleep(6)

sensor_thread=threading.Thread(target=update_sensor_data)
sensor_thread.daemon=True
sensor_thread.start()

def take_actions(temp,humidity,light):
    actions=[]
    if temp>40:
        actions.append("Ventilator pornit pentru racire")
    else:
        actions.append("Totul este in parametrii")
    if humidity>50:
        actions.append("Oprire sistem de irigare")
    else:
        actions.append("Totul este in parametrii")
    if light<40:
        actions.append("Pornire lumina artificiala")
    else:
        actions.append("Totul este in parametrii")


    return actions

@app.route("/")
def dashboard():
    temp=get_temperature()
    humidity=get_humidity()
    light=get_light()
    actions=take_actions(temp,humidity,light)

    return render_template(
        "index.html",
        temp=temp,
        humidity=humidity,
        light=light,
        actions=actions
    )

@socketio.on('connect')
def start_sensor_thread():
    socketio.start_background_task(update_sensor_data)
if __name__=="__main__":
    socketio.run(app,debug=True, allow_unsafe_werkzeug=True)