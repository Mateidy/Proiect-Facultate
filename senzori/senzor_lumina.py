import requests
import random
import time

SERVER_URL = "http://127.0.0.1:5000/sensor_data"

def generate_light():
    return round(random.uniform(0, 100), 2)


while True:
    light = generate_light()
    print(f"Generated light: {light}")

    time.sleep(2)

    data = {'sensor': 'light', 'value': light}

    retries = 3
    for attempt in range(retries):
        try:
            response = requests.post(SERVER_URL, json=data)
            if response.status_code == 200:
                print(f"Light data sent successfully: {light}")
                break
            else:
                print(f"Failed to send light data: {response.text}")
        except Exception as e:
            print(f"Error sending light data: {e}")

        time.sleep(5)

    time.sleep(10)
