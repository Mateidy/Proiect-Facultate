import requests
import random
import time

SERVER_URL = "http://127.0.0.1:5000/sensor_data"


def generate_humidity():
    return round(random.uniform(20, 90), 2)


while True:
    humidity = generate_humidity()
    print(f"Generated humidity: {humidity}")

    time.sleep(2)

    data = {'sensor': 'humidity', 'value': humidity}

    retries = 3
    for attempt in range(retries):
        try:
            response = requests.post(SERVER_URL, json=data)
            if response.status_code == 200:
                print(f"Humidity data sent successfully: {humidity}")
                break
            else:
                print(f"Failed to send humidity data: {response.text}")
        except Exception as e:
            print(f"Error sending humidity data: {e}")

        time.sleep(5)


    time.sleep(10)
