from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from bson.objectid import ObjectId
from mongoengine import connect, Q, Document, StringField, ListField, IntField, DateTimeField, BooleanField, ReferenceField
from datetime import datetime, timedelta
import random
import uuid
import json
from typing import List, Optional

from models import *

app = FastAPI()

# Configuration de la connexion à la base de données
connect(db='quiz_db', host='mongodb://localhost', port=27017)

# Déclaration des classes de modèles


class QuestionModel(BaseModel):
    # id: str
    # question: str
    # hint: Optional[str]
    # images: Optional[List[str]]
    # options: List[str]
    # answer: str
    # duration: int
    # created_by: str
    # created_at: datetime
    # modified_at: datetime
    # is_enable: bool

    id: Optional[str]
    question: str
    hint: Optional[str]
    images: Optional[List[str]]
    options: List[str]
    answer: str
    duration: int
    created_by: str
    created_at: datetime
    modified_at: datetime
    is_enable: bool


class ParticipantModel(BaseModel):
    id: str


# class ChallengeModel(BaseModel):
#     id: str
#     challenger: ParticipantModel
#     challenged: ParticipantModel
#     winner: ParticipantModel
#     is_started: bool
#     is_ended: bool
#     launched_date: datetime
#     accepted_date: datetime
#     ended_date: datetime
#     challenger_score: int
#     challenged_score: int
#     questions: list[QuestionModel]

# Déclaration des modèles MongoEngine


# class Question(Document):
#     id = StringField(primary_key=True, default=str(uuid.uuid4()))
#     question = StringField(required=True)
#     options = ListField(StringField(), required=True)
#     answer = StringField(required=True)
#     duration = IntField(default=5)

#     created_by = StringField(required=True)

#     created_at = DateTimeField(default=datetime.now)
#     modified_at = DateTimeField(default=datetime.now)

#     is_enable = BooleanField(default=True)

#     meta = {
#         'collection': 'questions'
#     }


class Participant(Document):
    id = StringField(primary_key=True)

    meta = {
        'collection': 'participants'
    }


# class Challenge(Document):
#     id = StringField(primary_key=True)
#     challenger = ReferenceField(Participant)
#     challenged = ReferenceField(Participant, default=None)
#     winner = ReferenceField(Participant, default=None)

#     is_started = BooleanField(default=True)
#     is_ended = BooleanField(default=False)

#     launched_date = DateTimeField(default=datetime.now)

#     accepted_date = DateTimeField(default=None)
#     ended_date = DateTimeField(default=None)

#     # Score des participants
#     challenger_score = IntField(default=0)
#     challenged_score = IntField(default=0)

#     questions = ListField(ReferenceField(Question), required=True)

#     meta = {
#         'collection': 'challenges'
#     }

# Routes pour les questions


# @app.get('/api/questions', response_model=List[QuestionModel])
# def get_questions():
#     questions = Question.objects()
#     return questions


# @app.post('/api/questions', response_model=QuestionModel)
# def create_question(question: QuestionModel):
#     question_obj = Question(**question.dict())
#     question_obj.save()
#     return question_obj


# @app.get('/api/questions/{question_id}', response_model=QuestionModel)
# def get_question(question_id: str):
#     try:
#         question = Question.objects.get(id=question_id)
#         return question
#     except Question.DoesNotExist:
#         raise HTTPException(status_code=404, detail='Question not found')


# @app.put('/api/questions/{question_id}', response_model=QuestionModel)
# def update_question(question_id: str, question: QuestionModel):
#     try:
#         question_obj = Question.objects.get(id=question_id)
#         question_obj.update(**question.dict())
#         return question_obj
#     except Question.DoesNotExist:
#         raise HTTPException(status_code=404, detail='Question not found')


# @app.delete('/api/questions/{question_id}')
# def delete_question(question_id: str):
#     try:
#         question = Question.objects.get(id=question_id)
#         question.delete()
#         return JSONResponse({'message': 'Question deleted successfully'})
#     except Question.DoesNotExist:
#         raise HTTPException(status_code=404, detail='Question not found')

# Routes pour les participants


@app.get("/api/questions", response_model=List[QuestionModel])
async def get_questions():
    questions = Question.objects()
    questions = json.loads(questions.to_json())
    return questions


@app.post("/api/questions")
def create_question(question: QuestionModel):
    question.save()
    return {"message": "Question created successfully"}


@app.get('/api/participants',)
def get_participants():
    participants = Participant.objects()
    participants = json.loads(participants.to_json())
    # print(participants.to_json())
    return participants


# @app.post('/api/participants', response_model=ParticipantModel)
# def create_participant(participant: ParticipantModel):
#     participant_obj = Participant(**participant.dict())
#     participant_obj.save()
#     return participant_obj


# @app.get('/api/participants/{participant_id}', response_model=ParticipantModel)
# def get_participant(participant_id: str):
#     try:
#         participant = Participant.objects.get(id=participant_id)
#         return participant
#     except Participant.DoesNotExist:
#         raise HTTPException(status_code=404, detail='Participant not found')


# @app.put('/api/participants/{participant_id}', response_model=ParticipantModel)
# def update_participant(participant_id: str, participant: ParticipantModel):
#     try:
#         participant_obj = Participant.objects.get(id=participant_id)
#         participant_obj.update(**participant.dict())
#         return participant_obj
#     except Participant.DoesNotExist:
#         raise HTTPException(status_code=404, detail='Participant not found')


# @app.delete('/api/participants/{participant_id}')
# def delete_participant(participant_id: str):
#     try:
#         participant = Participant.objects.get(id=participant_id)
#         participant.delete()
#         return JSONResponse({'message': 'Participant deleted successfully'})
#     except Participant.DoesNotExist:
#         raise HTTPException(status_code=404, detail='Participant not found')

# # Routes pour les défis


# @app.get('/api/challenges', response_model=List[ChallengeModel])
# def get_challenges():
#     challenges = Challenge.objects()
#     return challenges


# @app.get('/api/challenges/not-accepted/{participant_id}', response_model=List[ChallengeModel])
# def get_challenges_non_accepted(participant_id: str):
#     if not participant_id:
#         raise HTTPException(status_code=400, detail='Invalid participant ID')

#     deadline = datetime.now() - timedelta(hours=24)
#     challenges = Challenge.objects(
#         Q(challenged=None) | Q(launched_date__gte=deadline),
#         is_ended=False,
#         challenger__ne=participant_id
#     )
#     return challenges


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
    import uvicorn
    uvicorn.run("quiz2:app", host='localhost',
                port=5550, workers=1, reload=True)
