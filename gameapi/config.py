import os
import mongoengine
from dotenv import load_dotenv


# charger les variables d'environnement
load_dotenv()


# # Temps de rafraîchissement des top participants
# TOP_PARTICPANT_REFRESH_TIME = int(os.getenv('TOP_PARTICPANT_REFRESH_TIME'))
# # Temps d'attente avant l'envoi du message aux participants
# TOP_PARTICPANT_MESSAGE_WAIT_TIME = int(
#     os.getenv('TOP_PARTICPANT_MESSAGE_WAIT_TIME'))

# RANDOM_QUESTION_NUMBER = os.getenv('RANDOM_QUESTION_NUMBER')

# WEBSOCKET_SERVER_HOST = os.getenv('WEBSOCKET_SERVER_HOST')
# WEBSOCKET_SERVER_PORT = os.getenv('WEBSOCKET_SERVER_PORT')

db_name = os.getenv('MONGO_DB_NAME')
db_host = os.getenv('MONGO_DB_HOST')
db_port = int(os.getenv('MONGO_DB_PORT'))
db_username = os.getenv('MONGO_DB_USERNAME')
db_password = os.getenv('MONGO_DB_PASSWORD')

# Définir la configuration de connexion à MongoDB
mongoengine.connect(
    db=db_name,
    host=db_host,
    port=db_port,
    username=db_username,
    password=db_password,
)
