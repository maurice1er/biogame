from config import *
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Query
import base64

import uvicorn
from mongoengine import Q

from datetime import datetime, timedelta
import random
import json
import logging
from typing import Optional, List
import os

from models import *

from dotenv import load_dotenv


# charger les variables d'environnement
load_dotenv()


backend_port = int(os.getenv('BACKEND_PORT'))


app = FastAPI(
    title="BBio",
    description="""**Quiz Game**""",
    version="0.0.1",
    contact={
        "name": "Armel DREY",
        "email": "armeldrey@gmail.com",
    },
)

origins = [
    "http://localhost",
    "http://localhost:3001",
    "http://test.localhost:3001",
    "http://localhost:3000",
    "http://test.localhost:3000",
    "https://ec2-3-93-13-166.compute-1.amazonaws.com",
    "https://ec2-3-93-13-166.compute-1.amazonaws.com:8070"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Configuration de la connexion à la base de données
connect(db='quiz_db', host='mongodb://localhost', port=27017)

# Set up a custom logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


# Routes pour les questions

@app.get("/api/questions", response_model=List[QuestionModel], tags=["Questions"])
async def get_questions(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    """
    Get a paginated list of questions.

    **Parameters**:
    - `page` (int): Page number (default: 1)
    - `limit` (int): Maximum number of questions per page (default: 10)

    **Returns**:
    Paginated list of questions
    """

    skip = (page - 1) * limit
    questions = Question.objects.skip(skip).limit(limit).to_json()
    questions_json = json.loads(questions)

    return JSONResponse(content=questions_json)


@app.get("/api/questions/random", response_model=List[QuestionModel], tags=["Questions"])
async def get_random_questions(num_questions: int = 1):
    """
    Get a list of random questions.

    **Parameters**:
    - `num_questions` (int): Number of random questions to retrieve (default: 5)

    **Returns**:
    List of random questions
    """

    questions = Question.objects(is_enable=True).to_json()
    questions_json = json.loads(questions)

    random_questions = random.sample(questions_json, num_questions)
    return JSONResponse(content=random_questions)


@app.get('/api/questions/{question_id}', response_model=QuestionModel, tags=["Questions"])
def get_question(question_id: str):
    """
    Get a specific question based on its ID.

    **Parameters**:
    - `question_id` (str): ID of the question

    **Returns**:
    Corresponding question
    """

    try:
        question = Question.objects.get(id=question_id).to_json()
        question_json = json.loads(question)

        return JSONResponse(content=question_json)
    except Question.DoesNotExist:
        raise HTTPException(status_code=404, detail='Question not found')


@app.post('/api/questions', response_model=QuestionCreateModel, tags=["Questions"])
def create_question(question: QuestionCreateModel):
    """
    Create a new question.

    **Parameters**:
    - `question` (QuestionCreateModel): Data of the question to create

    **Returns**:
    Created question with generated ID
    """

    question_obj = Question(**question.dict())
    question_obj.save()

    try:
        question = Question.objects.get(id=question_obj.id).to_json()
        questions_json = json.loads(question)

        return JSONResponse(content=questions_json, status_code=201)
    except Question.DoesNotExist:
        raise HTTPException(status_code=404, detail='Question not found')


@app.put('/api/questions/{question_id}/upload_files', tags=["Questions"])
def upload_file(question_id: str, images: Optional[List[UploadFile]] = File(None)):
    """
    Update an existing question.

    **Parameters**:
    - `question_id` (str): ID of the question to update
    - `images` (List[UploadFile], optional): List of image files (multipart/form-data)

    **Returns**:
    Updated question
    """

    try:
        question_obj = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        raise HTTPException(status_code=404, detail='Question not found')

    try:
        for image in images:
            # Read image file
            image_content = image.file.read()
            # Encode image as base64 string
            encoded_image = base64.b64encode(image_content).decode('utf-8')
            # Append encoded image to the question's images list
            question_obj.images.append(encoded_image)

        # Mettre à jour la date de modification
        question_obj.modified_at = datetime.now

        question_obj.save()

        question = Question.objects.get(id=question_obj.id).to_json()
        question_json = json.loads(question)

        return JSONResponse(content=question_json, status_code=201)
    except:
        raise HTTPException(status_code=500, detail='Something is wrong')


@app.put('/api/questions/{question_id}', response_model=QuestionModel, tags=["Questions"])
def update_question(question_id: str, question: QuestionUpdateModel):
    """
    Update an existing question.

    **Parameters**:
    - `question_id` (str): ID of the question to update
    - `question` (QuestionUpdateModel): Updated data for the question

    **Returns**:
    Updated question
    """

    try:
        question_obj = Question.objects.get(id=question_id)

        update_data = question.dict(exclude_unset=True)
        question_obj.update(**update_data)

        # Mettre à jour la date de modification
        question_obj.modified_at = datetime.now
        question_obj.save()

        question = Question.objects.get(id=question_id).to_json()
        questions_json = json.loads(question)
        # questions_json = json.loads(question_obj.to_json())

        return JSONResponse(content=questions_json)
    except Question.DoesNotExist:
        raise HTTPException(status_code=404, detail='Question not found')


@app.delete('/api/questions/{question_id}', tags=["Questions"])
def delete_question(question_id: str):
    """
    Delete a question.

    **Parameters**:
    - `question_id` (str): ID of the question to delete

    **Returns**:
    JSON response with a success message
    """

    try:
        question = Question.objects.get(id=question_id)
        question.delete()
        return JSONResponse({'message': 'Question deleted successfully'})
    except Question.DoesNotExist:
        raise HTTPException(status_code=404, detail='Question not found')


# Routes pour les participants


@app.get('/api/participants', response_model=List[ParticipantModel], tags=["Participants"])
def get_participants(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    """
    Get a list of participants.

    **Parameters**:
    - `page` (int): Page number (default: 1)
    - `limit` (int): Number of participants per page (default: 10, min: 1, max: 100)

    **Returns**:
    List of participants
    """

    skip = (page - 1) * limit
    participants = Participant.objects.skip(skip).limit(limit).to_json()

    participants_json = json.loads(participants)

    return JSONResponse(content=participants_json)


@app.get('/api/participants/{participant_id}', response_model=ParticipantModel, tags=["Participants"])
def get_participant(participant_id: str):
    """
    Get a participant by ID.

    **Parameters**:
    - `participant_id` (str): ID of the participant

    **Returns**:
    Participant information
    """

    try:
        participant = Participant.objects.get(id=participant_id).to_json()
        participant_json = json.loads(participant)

        return JSONResponse(content=participant_json)
    except Participant.DoesNotExist:
        raise HTTPException(status_code=404, detail='Participant not found')


@app.post('/api/participants', response_model=ParticipantModel, tags=["Participants"])
def create_participant(participant: ParticipantModel):
    """
    Create a new participant.

    **Parameters**:
    - `participant` (ParticipantModel): Participant data

    **Returns**:
    Created participant
    """

    participant_obj = Participant(**participant.dict())
    participant_obj.save()

    try:
        participant = Participant.objects.get(id=participant_obj.id).to_json()
        participants_json = json.loads(participant)

        return JSONResponse(content=participants_json, status_code=201)
    except Participant.DoesNotExist:
        raise HTTPException(status_code=404, detail='Participant not found')


# @app.put('/api/participants/{participant_id}', response_model=ParticipantModel)
# def update_participant(participant_id: str, participant: ParticipantModel):
#     try:
#         participant_obj = Participant.objects.get(id=participant_id)
#         participant_obj.update(**participant.dict())
#         return participant_obj
#     except Participant.DoesNotExist:
#         raise HTTPException(status_code=404, detail='Participant not found')


# @app.delete('/api/participants/{participant_id}', response_model=ParticipantModel, tags=["Participants"])
# def delete_participant(participant_id: str):
#     try:
#         participant = Participant.objects.get(id=participant_id)
#         participant.delete()
#         return JSONResponse({'message': 'Participant deleted successfully'})
#     except Participant.DoesNotExist:
#         raise HTTPException(status_code=404, detail='Participant not found')


# Routes pour les défis


@app.get('/api/challenges', response_model=List[ChallengeModel], tags=["Challenges"])
def get_challenges(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    """
    Get a list of challenges.

    **Parameters**:
    - `page` (int): Page number (default: 1)
    - `limit` (int): Number of challenges per page (default: 10, min: 1, max: 100)

    **Returns**:
    List of challenges
    """

    skip = (page - 1) * limit
    challenges = Challenge.objects.skip(skip).limit(limit).to_json()

    challenges_json = json.loads(challenges)

    return JSONResponse(content=challenges_json)


@app.get('/api/challenges/not-accepted/{participant_id}', response_model=List[ChallengeModel], tags=["Challenges"])
def get_challenges_non_accepted(participant_id: str):
    """
    Get a list of challenges that have not been accepted.

    **Parameters**:
    - `participant_id` (str): ID of the participant

    **Returns**:
    List of challenges
    """

    if not participant_id:
        raise HTTPException(status_code=400, detail='Invalid participant ID')

    deadline = datetime.now() - timedelta(hours=24)
    challenges = Challenge.objects(
        Q(challenged=None) | Q(launched_date__gte=deadline),
        is_ended=False,
        challenger__ne=participant_id
    ).to_json()

    challenges_json = json.loads(challenges)

    return JSONResponse(content=challenges_json)


@app.get('/api/challenges/{challenge_id}', response_model=ChallengeModel, tags=["Challenges"])
def get_challenge(challenge_id: str):
    """
    Get a challenge by ID.

    **Parameters**:
    - `challenge_id` (str): ID of the challenge

    **Returns**:
    Challenge information
    """

    try:
        challenge = Challenge.objects.get(id=challenge_id).to_json()
        challenge_json = json.loads(challenge)

        return JSONResponse(content=challenge_json)
    except Challenge.DoesNotExist:
        raise HTTPException(status_code=404, detail='Challenge not found')


# @app.post('/api/challenges', response_model=ChallengeModel)
# def create_challenge(challenge: ChallengeModel):
#     challenge_obj = Challenge(**challenge.dict())
#     challenge_obj.save()
#     return challenge_obj


# @app.get('/api/challenges/{challenge_id}', response_model=ChallengeModel)
# def get_challenge(challenge_id: str):
#     try:
#         challenge = Challenge.objects.get(id=challenge_id)
#         return challenge
#     except Challenge.DoesNotExist:
#         raise HTTPException(status_code=404, detail='Challenge not found')


# @app.get('/api/challenges/{challenge_id}/questions', response_model=List[QuestionModel])
# def get_challenge_questions(challenge_id: str):
#     try:
#         challenge = Challenge.objects.get(id=challenge_id)
#         return challenge.questions
#     except Challenge.DoesNotExist:
#         raise HTTPException(status_code=404, detail='Challenge not found')


# @app.put('/api/challenges/{challenge_id}', response_model=ChallengeModel)
# def update_challenge(challenge_id: str, challenge: ChallengeModel):
#     try:
#         challenge_obj = Challenge.objects.get(id=challenge_id)
#         challenge_obj.update(**challenge.dict())
#         return challenge_obj
#     except Challenge.DoesNotExist:
#         raise HTTPException(status_code=404, detail='Challenge not found')


# # Autres routes

# @app.get('/')
# async def root():
#     return {'message': 'Welcome to the Quiz API'}
# # Montage des fichiers statiques
# # app.mount('/static', StaticFiles(directory='static'), name='static')
if __name__ == '__main__':
    print("Backend Server started --> [::]:5000")
    uvicorn.run("backend:app", host='https://biogame-production.up.railway.app',
                # log_level="info",
                port=backend_port, workers=1, reload=True)
