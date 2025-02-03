import subprocess
import time

# Pornim serverul FL
server_process = subprocess.Popen(["python", "federated_server.py"])
time.sleep(2)  # Așteptăm ca serverul să pornească

# Pornim clientul FL (senzor)
client_process = subprocess.Popen(["python", "senzori/federated_client.py"])
time.sleep(2)

# Pornim API-ul Flask
flask_process = subprocess.Popen(["python", "flask_api.py"])

# Așteptăm ca procesele să ruleze
server_process.wait()
client_process.wait()
flask_process.wait()
