import asyncio
import websockets
import random
import uuid
import requests
import os

from models import *

import mongoengine


# Temps de rafraîchissement des top participants (en secondes)
TOP_PARTICPANT_REFRESH_TIME = int(os.environ.get('TOP_REFRESH_TIME', 10))

# Temps d'attente avant l'envoi du message aux participants (en secondes)
TOP_PARTICPANT_MESSAGE_WAIT_TIME = int(os.environ.get('MESSAGE_WAIT_TIME', 15))

# Définir la configuration de connexion à MongoDB
mongoengine.connect(
    db='quiz_db',
    host='localhost',
    port=27017,
    username='',
    password='',
)


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
            await self.send_message(websocket, "Chemin non valide")

    async def handle_client_launch(self, websocket, path):
        # Demande d'identification du participant
        # await websocket.send("Veuillez vous identifier :")
        await self.send_message(websocket, "Veuillez vous identifier :")
        # participant_id = await websocket.recv()
        participant_id = await self.receive_message(websocket)

        # Vérification si le participant existe
        p_url = f"http://127.0.0.1:5000/api/participants/{participant_id}"
        p_req = requests.get(p_url)

        if p_req.status_code != 200:
            await self.send_message(websocket, "Erreur : le participant n'existe pas")
            return
        else:
            print(p_req.json())

        # Instanciation du participant challenger
        challenger = Participant.objects.get(id=participant_id)

        # Récupération des questions du défi
        questions = requests.get("http://127.0.0.1:5000/api/questions")
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
        await self.send_message(websocket, "Le jeu va commencer dans:")
        for i in [3, 2, 1]:
            await self.send_message(websocket, f"{i}s")
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
                await self.send_message(websocket, f"pour {duration}s")

                question_json = {"question": question['question']}
                await self.send_question(websocket, f"{question_json}")

                options_json = {"options": question['options']}
                await self.send_message(websocket, f"{options_json}")

                answer = await self.receive_message_with_timeout(websocket, duration)

                is_correct = await self.check_answers(websocket, answer, correct_answer)
                await self.process_score_launch(challenge, participant_id, is_correct)

                participant_score = self.get_participant_score_launch(
                    challenge, participant_id)
                await self.send_message(websocket, f"{idx+1}/{len(self.challenge_questions)} => score actuel : {participant_score}")

                score.score = participant_score
                score.save()

        finally:
            await self.send_message(websocket, f"Jeu  terminé")
            await self.handle_disconnect(participant_id)
            await self.emit_top_participants(websocket, path)

    async def handle_client_accept(self, websocket, path):
        # Demande d'identification du participant
        # await websocket.send("Veuillez vous identifier :")
        await self.send_message(websocket, "Veuillez vous identifier :")
        # participant_id = await websocket.recv()
        participant_id = await self.receive_message(websocket)

        # Vérification si le participant existe
        p_url = f"http://127.0.0.1:5000/api/participants/{participant_id}"
        p_req = requests.get(p_url)

        if p_req.status_code != 200:
            await self.send_message(websocket, "Erreur : le participant n'existe pas")
            return

        # # Instanciation du participant challenger
        # challenger = Participant.objects.get(id=participant_id)

        # Récupération des défis non acceptés
        challenges_url = f"http://127.0.0.1:5000/api/challenges/not-accepted/{participant_id}"
        challenges_req = requests.get(challenges_url)

        if challenges_req.status_code != 200:
            await self.send_message(websocket, "Erreur : impossible de récupérer la liste des défis")
            return

        challenges = challenges_req.json()

        if len(challenges) == 0:
            await self.send_message(websocket, "Aucun défi disponible.")
            return

        # Affichage des défis disponibles
        await self.send_message(websocket, "Liste des défis disponibles :")
        for challenge in challenges:
            await self.send_message(websocket, f"ID : {challenge['_id']}, Challenger : {challenge['challenger']}")

        # Réception du choix de défi de l'utilisateur
        await self.send_message(websocket, "Veuillez saisir l'ID du défi que vous souhaitez rejoindre :")
        # challenge_id = await websocket.recv()
        challenge_id = await self.receive_message(websocket)

        # Recherche du défi choisi
        chosen_challenge = None
        for challenge in challenges:
            if challenge['_id'] == challenge_id:
                chosen_challenge = challenge
                break

        if chosen_challenge is None:
            await self.send_message(websocket, "Erreur : défi invalide")
            return
        self.chosen_challenge = chosen_challenge
        self.challenge_questions = chosen_challenge['questions']

        # Instanciation du participant défié
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
                await self.send_message(websocket, f"pour {duration}s")

                await self.send_question(websocket, question['question'])
                answer = await self.receive_message_with_timeout(websocket, duration)

                is_correct = await self.check_answers(websocket, answer, correct_answer)
                await self.process_score_accept(challenge, participant_id, is_correct)

                participant_score = self.get_participant_score_accept(
                    challenge, participant_id)
                await self.send_message(websocket, f"{idx + 1}/{len(self.challenge_questions)} => score actuel : {participant_score}")

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

            await self.send_message(websocket, f"Jeu terminé")
            await self.handle_disconnect(participant_id)
            await self.emit_top_participants(websocket, path)

    async def emit_top_participants(self, websocket, path):
        # # Récupérer les 10 meilleurs participants en fonction de leur score
        # sc = Score.objects.order_by(
        #     '-score').only('participant', 'score').exclude('id').select_related('participant').limit(10)
        if path == "/top":
            while True:
                top_participants = {'top_participants': self.top_participants}
                await self.send_message(websocket, f"{top_participants}")
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

    async def send_question(self, websocket, question):
        await self.send_message(websocket, question)

    async def check_answers(self, websocket, answer, correct_answer):
        if answer == correct_answer:
            await self.send_message(websocket, f"Correct!")
            return True
        else:
            await self.send_message(websocket, f"Incorrect! The correct answer is {correct_answer}.")
            return False

    async def send_message(self, websocket, message):
        if websocket.closed:
            return None
        await websocket.send(message)

    async def receive_message(self, websocket):
        try:
            return await websocket.recv()
        except websockets.exceptions.ConnectionClosedOK:
            return None

    async def receive_message_with_timeout(self, websocket, duration):
        try:
            return await asyncio.wait_for(self.receive_message(websocket), timeout=duration)
        except asyncio.TimeoutError:
            return None
        except websockets.exceptions.ConnectionClosedOK:
            return None

    async def start(self, host, port):
        async with websockets.serve(self.handle_client, host, port):
            print("Quiz Game server started.")
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
    await game_server.start("localhost", 8527)

if __name__ == "__main__":
    asyncio.run(main())
