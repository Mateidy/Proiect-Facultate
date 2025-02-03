import subprocess
import time

server_process = subprocess.Popen(["python", "federated_server.py"])
time.sleep(2)

client_process = subprocess.Popen(["python", "senzori/federated_client.py"])
time.sleep(2)

flask_process = subprocess.Popen(["python", "flask_api.py"])

server_process.wait()
client_process.wait()
flask_process.wait()
