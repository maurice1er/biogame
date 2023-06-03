import time
import subprocess

if __name__ == "__main__":
    # Lancer le script main-launch.py dans un autre processus séparé
    launch_process = subprocess.Popen(["python", "quiz.py"])

    # Lancer le script main-accept.py dans un processus séparé
    accept_process = subprocess.Popen(["python", "websocket.py"])

    # Attendre la fin des deux processus
    accept_process.wait()

    time.sleep(5)

    launch_process.wait()
