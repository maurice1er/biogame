#!/bin/bash

# 
source socket/bin/activate

# Lancer le serveur gRPC usermanagement_server.py dans un autre processus séparé
python3 usermanagement_server.py &

# Lancer le script backend quiz.py dans un autre processus séparé
python3 backend.py &

# Lancer le socket dans un autre processus séparé
python3 wsgrpc.py &

# Attendre la fin des processus
wait
