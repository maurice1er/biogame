import time
import subprocess

if __name__ == "__main__":
    # Lancer le serveur gRPC usermanagement_server.py dans un autre processus séparé
    grpc_server_process = subprocess.Popen(
        ["python", "usermanagement_server.py"])

    # Lancer le script backend quiz.py dans un autre processus séparé
    launch_process = subprocess.Popen(["python", "quiz.py"])

    # Lancer le script main-accept.py dans un processus séparé
    accept_process = subprocess.Popen(["python", "wsgrpc.py"])

    # Attendre la fin des deux processus
    grpc_server_process()
    time.sleep(3)

    accept_process.wait()
    time.sleep(3)

    launch_process.wait()
