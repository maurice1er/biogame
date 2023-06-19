import asyncio
import websockets
import random
import uuid
import requests
import json


import grpc
from mygRPC import usermanagement_pb2 as usermanagement_pb2
from mygRPC import usermanagement_pb2_grpc as usermanagement_pb2_grpc

from models import *

from config.config import *


# gRPC clients


def check_user_existence(participant_id):
    channel = grpc.insecure_channel('localhost:50051')
    stub = usermanagement_pb2_grpc.UserServiceStub(channel)

    request = usermanagement_pb2.UserExistenceRequest(
        participant_id=participant_id)
    response = stub.CheckUserExistence(request)
    user_exists = response.user_exists

    if user_exists == True:
        res = {"state": True, "status": 200}
    else:
        res = {"state": False, "status": 500}
    return res


def get_challenge_questions():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = usermanagement_pb2_grpc.UserServiceStub(channel)
        request = usermanagement_pb2.ChallengeQuestionsRequest()
        response = stub.GetChallengeQuestions(request)
        return response.questions

# insert into response collection


def insert_challenge_response(challenge_id, participant_id, question_id, response, is_correct):

    try:
        challenge_id = Challenge.objects.get(id=challenge_id)
        participant_id = Participant.objects.get(id=participant_id)
        question_id = Question.objects.get(id=question_id)

        if response == None:
            response = ""
        else:
            response = response['answer']

        response = ChallengeReponse(
            challenge=challenge_id,
            participant=participant_id,
            question=question_id,
            reponse=response
        )
        response.is_correct = is_correct
        response.save()
    except Exception as e:
        print("error to inserted into Response collection")


class QuizGameServer:
    def __init__(self):
        self.participants = {}
        self.questions = []
        self.challenge_questions = []
        self.counter = 0

        self.chosen_challenge = None

        self.top_participants = []

    # handle client

    async def handle_client(self, websocket, path):
        if path == "/accept":
            await self.handle_client_accept(websocket, path)
        elif path == "/launch":
            await self.handle_client_launch(websocket, path)
        elif path == "/top":
            await self.emit_top_participants(websocket, path)
        else:
            # await websocket.send("Chemin non valide")
            await self.send_json_message_with_status(websocket, "message", "Chemin non valide")

    async def handle_client_launch(self, websocket, path):
        # Demande d'identification du participant
        await self.send_json_message_with_status(websocket, "message", "Veuillez vous identifier")

        try:
            _participant = await self.receive_message(websocket)
            participant_id = _participant["participant_id"]
        except:
            raise ("Particpant Id error!")

        # Vérification si le participant existe
        user_exists = check_user_existence(participant_id)
        print(f"User exists: {user_exists}")

        if user_exists['state'] == False:
            await self.send_json_message_with_status(websocket, "message", "identification incorrect", status=user_exists['status'])
            return

        await self.send_json_message_with_status(websocket, "message", "identification correct")

        # Instanciation du participant challenger
        try:
            challenger = Participant.objects.get(id=participant_id)
        except Participant.DoesNotExist:
            create_participant_url = f"http://127.0.0.1:8000/api/participants"
            requests.post(create_participant_url, json={"id": participant_id})
            challenger = Participant.objects.get(id=participant_id)

        # Récupération des questions aleatoirelement du défi
        random_question_url = f"http://localhost:8000/api/questions/random?num_questions={RANDOM_QUESTION_NUMBER}"
        questions = requests.get(random_question_url)
        if questions.status_code == 200:
            self.questions = questions.json()

        self.challenge_questions = random.sample(self.questions, 3)

        # Création du défi
        challenge = Challenge(
            id=str(uuid.uuid4()),
            challenger=challenger,
            is_started=True,
            questions=self.challenge_questions
        )
        challenge.save()

        # Démarrage du défi
        await self.send_json_message(websocket, "message", "Le jeu va commencer dans 3s")
        for i in [3, 2, 1]:
            # - await self.send_message(websocket, f"{i}s")
            await asyncio.sleep(1)

        score = Score()
        score.challenge = Challenge.objects.get(id=challenge.id)
        score.participant = challenger
        score.is_challenger = True
        score.save()

        try:
            for (idx, question) in enumerate(self.challenge_questions):
                correct_answer = question['answer']
                duration = question['duration']
                # await self.send_json_message_with_status(websocket, "duration", f"{duration}")

                # question_json = {"question": question['question']}
                # await self.send_question(websocket, f"{question_json}")
                quizz = {
                    "question": question['question'],
                    "options": question['options'],
                    "duration": duration
                }

                # await self.send_json_message_with_status(websocket, "question", f"{question['question']}")

                # options_json = {"options": question['options']}
                # await self.send_json_message_with_status(websocket, "options", f"{question['options']}")

                # await self.send_json_message(websocket, "quizz", quizz)
                await self.send_json_message(websocket, "quizz", quizz)

                answer = await self.receive_message_with_timeout(websocket, duration)

                is_correct = await self.check_answers(websocket, answer, correct_answer)
                await self.process_score_launch(challenge, participant_id, is_correct)

                insert_challenge_response(
                    challenge.id, participant_id, question['_id'], answer, is_correct)

                participant_score = self.get_participant_score_launch(
                    challenge, participant_id)
                # - await self.send_message(websocket, f"{idx+1}/{len(self.challenge_questions)} => score actuel : {participant_score}")

                score.score = participant_score
                score.save()

        finally:
            await self.send_json_message_with_status(websocket, "end", True)
            await self.handle_disconnect(participant_id)
            await self.emit_top_participants(websocket, path)

    async def handle_client_accept(self, websocket, path):
        # Demande d'identification du participant
        await self.send_json_message_with_status(websocket, "message", "Veuillez vous identifier")
        # participant_id = await websocket.recv()
        # participant_id = await self.receive_message(websocket)

        _participant = await self.receive_message(websocket)

        participant_id = _participant["participant_id"]
        print(_participant)
        print(" ")

        # Vérification si le participant existe
        user_exists = check_user_existence(participant_id)
        print(f"User exists: {user_exists}")

        if user_exists['state'] == False:
            await self.send_json_message_with_status(websocket, "message", "identification incorrect", status=user_exists['status'])
            return

        await self.send_json_message_with_status(websocket, "message", "identification correct")

        # Récupération des défis non acceptés
        challenges_url = f"http://127.0.0.1:8000/api/challenges/not-accepted/{participant_id}"
        challenges_req = requests.get(challenges_url)

        if challenges_req.status_code != 200:
            await self.send_json_message_with_status(websocket, "Erreur", "impossible de récupérer la liste des defis", status=500)
            return

        challenges = challenges_req.json()

        if len(challenges) == 0:
            await self.send_json_message_with_status(websocket, "message", "Aucun defi disponible.")
            return

        # Affichage des défis disponibles
        await self.send_json_message_with_status(websocket, "message", "Liste des defis disponibles.")
        for challenge in challenges:
            chg = {"id": challenge['_id'],
                   "challenger": challenge['challenger']}
            await self.send_message(websocket, f"{chg}")

        # Réception du choix de défi de l'utilisateur
        await self.send_json_message_with_status(websocket, "message", "Veuillez saisir l'ID du défi que vous souhaitez rejoindre")
        # challenge_id = await websocket.recv()
        _challenge = await self.receive_message(websocket)
        challenge_id = _challenge["challenge_id"]

        # Recherche du défi choisi
        chosen_challenge = None
        for challenge in challenges:
            if challenge['_id'] == challenge_id:
                chosen_challenge = challenge
                break

        if chosen_challenge is None:
            await self.send_json_message_with_status(websocket, "message", "défi invalide", status=500)
            return
        self.chosen_challenge = chosen_challenge
        self.challenge_questions = chosen_challenge['questions']

        # Instanciation du participant challenged
        try:
            challenged = Participant.objects.get(id=participant_id)
        except Participant.DoesNotExist:
            create_participant_url = f"http://127.0.0.1:8000/api/participants"
            requests.post(create_participant_url, json={"id": participant_id})
            challenged = Participant.objects.get(id=participant_id)

        challenge = Challenge.objects.get(id=chosen_challenge['_id'])
        challenge.challenged = challenged
        challenge.accepted_date = f'{datetime.utcnow()}'
        challenge.save()

        # Démarrage du défi
        await self.send_message(websocket, "Le jeu va commencer dans :")
        for i in [3, 2, 1]:
            await self.send_message(websocket, f"{i}s")
            await asyncio.sleep(1)

        score = Score()
        score.challenge = Challenge.objects.get(id=challenge.id)
        score.participant = challenged
        score.is_challenger = False
        score.save()

        try:
            for (idx, question) in enumerate(self.challenge_questions):
                correct_answer = question['answer']
                duration = question['duration']
                await self.send_json_message_with_status(websocket, "duration", f"{duration}s")

                # await self.send_question(websocket, question['question'])
                await self.send_json_message_with_status(websocket, "question", f"{question['question']}")
                answer = await self.receive_message_with_timeout(websocket, duration)

                is_correct = await self.check_answers(websocket, answer, correct_answer)
                await self.process_score_accept(challenge, participant_id, is_correct)

                insert_challenge_response(
                    challenge.id, participant_id, question['_id'], answer, is_correct)

                participant_score = self.get_participant_score_accept(
                    challenge, participant_id)

                # score_actuel = f"{idx+1}/{len(self.challenge_questions)} => score actuel : {participant_score}"
                await self.send_json_message(websocket, "score_actuel", participant_score)

                score.score = participant_score
                score.save()

        finally:
            challenge.is_ended = True
            challenge.ended_date = f'{datetime.utcnow()}'

            # set winner
            if challenge.challenger_score < challenge.challenged_score:
                challenge.winner = challenge.challenged
            elif challenge.challenger_score > challenge.challenged_score:
                challenge.winner = challenge.challenger
            else:
                pass

            score = Score()
            score.challenge = Challenge.objects.get(id=challenge.id)
            score.participant = Participant.objects.get(id=participant_id)
            challenge.save()

            await self.send_json_message_with_status(websocket, "end", True)
            await self.handle_disconnect(participant_id)
            await self.emit_top_participants(websocket, path)

    async def emit_top_participants(self, websocket, path):
        # # Récupérer les 10 meilleurs participants en fonction de leur score
        # sc = Score.objects.order_by(
        #     '-score').only('participant', 'score').exclude('id').select_related('participant').limit(10)
        if path == "/top":
            while True:
                await self.send_json_message(websocket, "top_participants", self.top_participants)
                await asyncio.sleep(TOP_PARTICPANT_MESSAGE_WAIT_TIME)

    def update_top_participants(self):
        # Requête pour regrouper par participant et filtrer par score
        pipeline = [
            {"$group": {
                "_id": "$participant",
                "total_score": {"$sum": "$score"}
            }},
            {"$sort": {
                "total_score": -1  # Trie par score décroissant
            }},
            # {"$match": {
            #     # Filtrer par score supérieur à 0 (ajustez selon vos critères)
            #     "max_score": {"$gt": 0}
            # }},
            {"$limit": 10}  # Limiter les résultats aux 10 premiers participants
        ]

        results = Score.objects.aggregate(*pipeline)
        self.top_participants = [
            {
                'id': result["_id"],
                'score': result["total_score"],
            }
            for result in results
        ]

    # difference

    async def process_score_accept(self, challenge, participant_id, is_correct):
        if is_correct:
            if challenge.challenged and str(challenge.challenged.id) == participant_id:
                challenge.challenged_score += 10
            challenge.save()
            # await self.emit_top_participants()

    def get_participant_score_accept(self, challenge, participant_id):
        if challenge.challenged and str(challenge.challenged.id) == participant_id:
            return challenge.challenged_score
        return 0

    async def process_score_launch(self, challenge, participant_id, is_correct):
        if is_correct:
            if challenge.challenger and str(challenge.challenger.id) == participant_id:
                challenge.challenger_score += 10
            challenge.save()
            # await self.emit_top_participants()

    def get_participant_score_launch(self, challenge, participant_id):
        if challenge.challenger and str(challenge.challenger.id) == participant_id:
            return challenge.challenger_score
        return 0

    # commoms
    async def handle_disconnect(self, participant_id):
        if participant_id in self.participants:
            score = self.participants[participant_id]['score']
            websocket = self.participants[participant_id]['websocket']

            await self.send_message(websocket, f"{participant_id} => Votre score final est : {score}")

            del self.participants[participant_id]
            print(f"Participant {participant_id} déconnecté.")

    async def send_initial_message(self, websocket, participant_id):
        initial_message = f"Welcome, participant {participant_id},\nThe Quiz Game is about to start."
        await self.send_message(websocket, initial_message)
        self.counter += 1

    # async def send_question(self, websocket, question):
    #     await self.send_message(websocket, question)

    async def check_answers(self, websocket, answer, correct_answer):

        if answer == None:
            return False
        if answer['answer'] == correct_answer:
            value = f"Correct!"
            await self.send_json_message_with_status(websocket, "message", value)

            return True
        else:
            value = f"Incorrect! The correct answer is {correct_answer}."
            await self.send_json_message_with_status(websocket, "message", value)

            return False

    async def send_message(self, websocket, message):
        if websocket.closed:
            return None

        await websocket.send(message)

    async def send_json_message(self, websocket, key, value):
        if websocket.closed:
            return None

        json_message = {key: value}
        json_string = json.dumps(json_message)
        await websocket.send(json_string)

    async def send_json_message_with_status(self, websocket, key, value, status=200):
        if websocket.closed:
            return None

        json_message = {key: value, "status": status}
        json_string = json.dumps(json_message)
        await websocket.send(json_string)

    async def receive_json_message(self, websocket):
        try:
            response = await websocket.recv()
            return response
        except websockets.exceptions.ConnectionClosedOK:
            return None
        except json.decoder.JSONDecodeError as err:
            error_message = {"error": "Invalid JSON response"}
            await websocket.send(f"{error_message}")
            return

    async def receive_message(self, websocket):
        try:
            response = await websocket.recv()
            print(" ")
            print(type(response))
            print(" ")
            json_response = json.loads(response)
            return json_response
        except websockets.exceptions.ConnectionClosedOK:
            return None
        except json.decoder.JSONDecodeError as err:
            error_message = {"error": "Invalid JSON response"}
            await websocket.send(f"{error_message}")
            return

    async def receive_message_with_timeout(self, websocket, duration):
        try:
            return await asyncio.wait_for(self.receive_message(websocket), timeout=duration)
        except asyncio.TimeoutError:
            return None
        except websockets.exceptions.ConnectionClosedOK:
            return None

    async def start(self, host, port):
        async with websockets.serve(self.handle_client, host, port):
            print("Socket Server started --> ws://[::]:8527")
            await asyncio.Future()  # Keep the server running indefinitely

    def stop(self):
        print("Quiz Game server stopped.")

    # Mettre à jour les meilleurs participants toutes les 5 secondes
    async def refresh_top_participants(self):
        while True:
            self.update_top_participants()
            await asyncio.sleep(TOP_PARTICPANT_REFRESH_TIME)


# if __name__ == "__main__":
#     server = QuizGameServer()
#     print("localhost:8527")

#     # Mettre à jour les meilleurs participants toutes les 10 secondes
#     asyncio.create_task(server.refresh_top_participants())

#     await asyncio.run(server.start("localhost", 8527))


async def main():
    game_server = QuizGameServer()

    # Mettre à jour les meilleurs participants toutes les 5 secondes
    asyncio.create_task(game_server.refresh_top_participants())

    # Démarrer le serveur de jeu
    await game_server.start(WEBSOCKET_SERVER_HOST, WEBSOCKET_SERVER_PORT)

if __name__ == "__main__":
    asyncio.run(main())
