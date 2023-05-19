from mongoengine import Document, StringField, ListField, IntField, DateTimeField, BooleanField, ReferenceField
from datetime import datetime
import json
import uuid
import random


class Question(Document):
    id = StringField(primary_key=True, default=str(uuid.uuid4()))
    question = StringField(required=True)
    options = ListField(StringField(), required=True)
    answer = StringField(required=True)
    duration = IntField(default=7)

    created_by = StringField(required=True)

    created_at = DateTimeField(default=datetime.now)
    modified_at = DateTimeField(default=datetime.now)

    is_enable = BooleanField(default=True)

    meta = {
        'collection': 'questions'
    }


class Participant(Document):
    name = StringField(required=True)
    score = IntField(default=0)

    meta = {
        'collection': 'participants'
    }


class Challenge(Document):
    id = StringField(primary_key=True)
    challenger = ReferenceField('Participant')
    challenged = ReferenceField('Participant')
    winner = StringField(required=True)
    challenge_date = DateTimeField(required=True)
