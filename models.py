from mongoengine import Document, StringField, ListField, IntField, DateTimeField, BooleanField, ReferenceField
from datetime import datetime
import uuid


class Question(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    question = StringField(required=True)
    options = ListField(StringField(), required=True)
    answer = StringField(required=True)
    duration = IntField(default=5)

    created_by = StringField(required=True)

    created_at = DateTimeField(default=datetime.now)
    modified_at = DateTimeField(default=datetime.now)

    is_enable = BooleanField(default=True)

    meta = {
        'collection': 'questions'
    }


class Participant(Document):
    id = StringField(primary_key=True)

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
