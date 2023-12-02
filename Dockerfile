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

# Définissez les variables d'environnement
ENV MONGODB_URI=

ENV PORT=3000
ENV RANDOM_QUESTIONS=3
ENV JWT_TOKEN_SECRET=

ENV CONSUL_IP=
ENV CONSUL_PORT=

# Exposez le port sur lequel votre application Node.js écoute
EXPOSE $PORT

# Commande pour démarrer l'application lorsque le conteneur démarre
# CMD ["node", "index.js"]
CMD ["npm", "run", "dev"]

