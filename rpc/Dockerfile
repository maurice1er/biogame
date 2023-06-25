# Utilisez une image Python de base
FROM python:3.9-slim

# Copiez les fichiers du serveur gRPC dans le conteneur
# COPY . /usr/src/app
WORKDIR /usr/src/app

# Installez les dépendances du serveur gRPC
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
COPY . . 

# Exposez le port du serveur gRPC
EXPOSE 50051

# Démarrez le serveur gRPC
CMD ["python3", "server.py"]
