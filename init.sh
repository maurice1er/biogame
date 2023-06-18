#!/bin/bash

# 
source socket/bin/activate

# Lancer le serveur gRPC usermanagement_server.py dans un autre processus séparé
python usermanagement_server.py &

# Lancer le script backend quiz.py dans un autre processus séparé
python backend.py &

# Lancer le socket dans un autre processus séparé
python wsgrpc.py &

# Attendre la fin des processus
wait
