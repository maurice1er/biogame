from mongoengine import connect, Q, Document, StringField, ListField, IntField, DateTimeField, BooleanField, ReferenceField
from datetime import datetime
import uuid
from typing import List, Optional
from fastapi import UploadFile, File

from pydantic import BaseModel

# Mongo


class Question(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    question = StringField(required=True)
    hint = StringField(required=False)

    images = ListField(StringField(), required=False)

    options = ListField(StringField(), required=True)
    answer = StringField(required=True)
    duration = IntField(default=10)

    created_by = StringField(required=True)

    created_at = DateTimeField(default=datetime.now)
    modified_at = DateTimeField(default=datetime.now)

    is_enable = BooleanField(default=True)

    meta = {
        'collection': 'questions'
    }


class Participant(Document):
    id = StringField(primary_key=True)
    # is_blocked = BooleanField(default=False)
    # is_denied = BooleanField(default=False)

    meta = {
        'collection': 'participants'
    }


class Challenge(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))

    challenger = ReferenceField(Participant)
    challenged = ReferenceField(Participant, default=None)
    winner = ReferenceField(Participant, default=None)

    is_started = BooleanField(default=True)
    is_ended = BooleanField(default=False)

    launched_date = DateTimeField(default=datetime.now)

    accepted_date = DateTimeField(default=None)
    ended_date = DateTimeField(default=None)

    # Score des participants
    challenger_score = IntField(default=0)
    challenged_score = IntField(default=0)

    questions = ListField(ReferenceField(Question), required=True)

    meta = {
        'collection': 'challenges'
    }


class Score(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    challenge = ReferenceField('Challenge', required=True)
    participant = ReferenceField('Participant')
    score = IntField(default=0)

    is_challenger = BooleanField(default=False)

    meta = {
        'collection': 'scores'
    }


class ChallengeReponse(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    challenge = ReferenceField('Challenge', required=True)
    participant = ReferenceField('Participant', required=True)
    question = ReferenceField('Question')
    reponse = StringField(required=False)
    is_correct = BooleanField(default=False)

    meta = {
        'collection': 'challenge_responses'
    }


# FastAPI


class QuestionModel(BaseModel):
    id: Optional[str]
    question: str
    hint: Optional[str]
    images: Optional[List[str]]
    options: List[str]
    answer: str
    duration: int
    created_by: str
    created_at: Optional[datetime]
    modified_at: Optional[datetime]
    is_enable: bool


class QuestionCreateModel(BaseModel):
    question: str
    hint: Optional[str]
    # images: Optional[List[str]]
    options: List[str]
    answer: str
    duration: int
    created_by: str
    # is_enable: bool


class QuestionUpdateModel(BaseModel):
    question: Optional[str]
    hint: Optional[str]
    images: Optional[List[str]]
    options: Optional[List[str]]
    answer: Optional[str]
    duration: Optional[int]
    is_enable: Optional[bool]


class ParticipantModel(BaseModel):
    id: str
    # is_blocked: bool
    # is_denied: bool


class ChallengeModel(BaseModel):
    id: str
    challenger: ParticipantModel
    challenged: Optional[ParticipantModel]
    winner: Optional[ParticipantModel]
    is_started: bool = True
    is_ended: bool = False
    launched_date: datetime
    accepted_date: Optional[datetime]
    ended_date: Optional[datetime]
    challenger_score: int
    challenged_score: int
    questions: list[QuestionModel]
