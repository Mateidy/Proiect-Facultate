import subprocess

sensor_scripts = [
    "senzori/senzor_temperatura.py",
    "senzori/senzor_umiditate.py",
    "senzori/senzor_lumina.py"
]

processes = []
for script in sensor_scripts:
    processes.append(
        subprocess.Popen([r"C:\Users\costi\PycharmProjects\Proiect_Facultate\.venv\Scripts\python.exe", script]))


try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    for p in processes:
        p.terminate()
