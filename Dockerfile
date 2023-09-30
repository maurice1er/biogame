# Utilisez l'image Node.js 14 comme image de base
FROM node:14

# Créez et définissez le répertoire de travail dans le conteneur
WORKDIR /usr/src/app

# Copiez le package.json et le package-lock.json dans le répertoire de travail
COPY package*.json ./

# Installez les dépendances
RUN npm install -y

# Copiez le reste des fichiers de l'application dans le répertoire de travail
COPY . .

# Exposez le port sur lequel l'application fonctionne
EXPOSE 8080

# Commande pour démarrer l'application lorsque le conteneur démarre
CMD ["node", "app.js"]
