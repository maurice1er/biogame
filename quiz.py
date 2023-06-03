from flask import Flask, request, jsonify, abort
from flask_socketio import SocketIO, emit
from bson.objectid import ObjectId
from mongoengine import connect, register_connection
from flask_swagger_ui import get_swaggerui_blueprint
import random
from pymongo import MongoClient
from pymongo.errors import AutoReconnect

from tenacity import retry, stop_after_attempt, wait_fixed
from mongoengine import Q
import mongoengine

from datetime import datetime, timedelta
import time
from models import Question, Participant, Challenge


app = Flask(__name__)

app.config['SECRET_KEY'] = 'your-secret-key'
# app.config['MONGODB_SETTINGS'] = {
#     'db': 'quiz_db',
#     'host': 'mongodb://localhost',
#     'port': 27017
# }

mongoengine.connect(
    db='quiz_db',
    host='localhost',
    port=27017,
    username='',
    password='',
)


# Chemin vers le fichier YAML de spécification Swagger
swagger_yaml = './static/swagger.yaml'

# Configuration de l'extension SwaggerUI
SWAGGER_URL = '/api/docs'  # URL pour accéder à la documentation Swagger
# URL vers le fichier YAML de spécification Swagger
API_URL = '/static/swagger.yaml'

# Création du blueprint SwaggerUI
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "BBio Game",  # Nom de votre API
        # Chargement du fichier YAML de spécification Swagger
        'spec': open(swagger_yaml).read()
    }
)

# Enregistrement du blueprint dans l'application Flask
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


socketio = SocketIO(app)


# Routes pour les questions


@app.route('/api/questions', methods=['GET'])
def get_questions():
    questions = Question.objects()
    return questions.to_json()


@app.route('/api/questions', methods=['POST'])
def create_question():
    question_data = request.get_json()
    print(question_data)
    question = Question(**question_data)
    question.created_by = "cf9e6aa4-d879-422d-b26d-8fac11cde5bf"
    question.save()
    return question.to_json(), 201


@app.route('/api/questions/<question_id>', methods=['GET'])
def get_question(question_id):
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return jsonify({'message': 'Question not found'}), 404

    return question.to_json()


@app.route('/api/questions/<question_id>', methods=['PUT'])
def update_question(question_id):
    question_data = request.get_json()
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return jsonify({'message': 'Question not found'}), 404

    question.update(**question_data)
    return jsonify({'message': 'Question updated successfully'})


@app.route('/api/questions/<question_id>', methods=['DELETE'])
def delete_question(question_id):
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return jsonify({'message': 'Question not found'}), 404

    question.delete()
    return jsonify({'message': 'Question deleted successfully'})

# Routes pour les participants


@app.route('/api/participants', methods=['GET'])
def get_participants():
    participants = Participant.objects()
    return participants.to_json()


@app.route('/api/participants', methods=['POST'])
def create_participant():
    participant_data = request.get_json()
    participant = Participant(**participant_data)
    participant.save()
    return participant.to_json(), 201


@app.route('/api/participants/<participant_id>', methods=['GET'])
def get_participant(participant_id):
    try:
        participant = Participant.objects.get(id=participant_id)
    except Participant.DoesNotExist:
        return jsonify({'message': 'Participant not found'}), 404

    return participant.to_json()


@app.route('/api/participants/<participant_id>', methods=['PUT'])
def update_participant(participant_id):
    participant_data = request.get_json()
    try:
        participant = Participant.objects.get(id=participant_id)
    except Participant.DoesNotExist:
        return jsonify({'message': 'Participant not found'}), 404

    participant.update(**participant_data)
    return jsonify({'message': 'Participant updated successfully'})


@app.route('/api/participants/<participant_id>', methods=['DELETE'])
def delete_participant(participant_id):
    try:
        participant = Participant.objects.get(id=participant_id)
    except Participant.DoesNotExist:
        return jsonify({'message': 'Participant not found'}), 404

    participant.delete()
    return jsonify({'message': 'Participant deleted successfully'})


@app.route('/api/challenges', methods=['GET'])
def get_challenges():
    challenges = Challenge.objects()
    return challenges.to_json()


@app.route('/api/challenges/not-accepted/<participant_id>', methods=['GET'])
def get_challenges_non_accepted(participant_id):
    if not participant_id:
        return jsonify({'message': 'Invalid participant ID'}), 400

    # Calculer la date limite (24 heures avant maintenant)
    deadline = datetime.now() - timedelta(hours=24)

    # Récupérer les défis non acceptés dans la limite de temps
    challenges = Challenge.objects(
        Q(challenged=None) | Q(launched_date__gte=deadline),
        is_ended=False,
        challenger__ne=participant_id
    )

    return challenges.to_json()


@app.route('/api/challenges', methods=['POST'])
def create_challenges():
    challenge_data = request.get_json()
    challenge = Challenge(**challenge_data)
    challenge.save()
    return challenge.to_json(), 201


@app.route('/api/challenges/<challenges_id>', methods=['GET'])
def get_challenge(challenges_id):
    try:
        challenges = Challenge.objects.get(id=challenges_id)
    except Challenge.DoesNotExist:
        return jsonify({'message': 'Challenge not found'}), 404

    return challenges.to_json()


@app.route('/api/challenges/<challenges_id>/questions', methods=['GET'])
def get_challenge_questions(challenges_id):
    try:
        challenges = Challenge.objects.get(id=challenges_id)
    except Challenge.DoesNotExist:
        return jsonify({'message': 'Challenge not found'}), 404

    return challenges.questions.to_json()


@app.route('/api/challenges/<challenge_id>', methods=['PUT'])
def update_challenge(challenge_id):
    try:
        challenge_data = request.get_json()
        update_fields = {}
        for key, value in challenge_data.items():
            update_fields[key] = value

        Challenge.objects(id=challenge_id).update_one(**update_fields)

        return jsonify({'message': 'Challenge updated successfully'})

    except Challenge.DoesNotExist:
        return jsonify({'message': 'Défi non trouvé'}), 404
    except Participant.DoesNotExist:
        return jsonify({'message': 'Participant non trouvé'}), 404
    except Exception as e:
        return jsonify({'message': 'Erreur lors de la mise à jour du défi', 'error': str(e)}), 500


if __name__ == '__main__':
    socketio.run(app)
    # socketio.run(app, debug=True)
