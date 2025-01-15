import requests
import random
import time

SERVER_URL = "http://127.0.0.1:5000/sensor_data"


def generate_temperature():
    return round(random.uniform(15, 45), 2)


while True:
    temperature = generate_temperature()
    print(f"Generated temperature: {temperature}")


    time.sleep(2)

    data = {'sensor': 'temperature', 'value': temperature}

    retries = 3
    for attempt in range(retries):
        try:
            response = requests.post(SERVER_URL, json=data)
            if response.status_code == 200:
                print(f"Temperature data sent successfully: {temperature}")
                break
            else:
                print(f"Failed to send temperature data: {response.text}")
        except Exception as e:
            print(f"Error sending temperature data: {e}")

        time.sleep(5)

    time.sleep(10)
