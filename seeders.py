import mongoengine
import time
from models import Question, Challenge, Score, Participant

# Définir la configuration de connexion à MongoDB
mongoengine.connect(
    db='quiz_db',
    host='localhost',
    port=27017,
    username='',
    password='',
)

# Liste des questions à insérer
questions_list = [
    {
        "question": "Quel est le processus de conversion des matières organiques en compost riche en éléments nutritifs ?",
        "options": [
            "Fumigation",
            "Amendement",
            "Biodégradation",
            "Compostage"
        ],
        "answer": "Compostage",
        "duration": 10
    },
    {
        "question": "Qu'est-ce que la photosynthèse ?",
        "options": [
            "Le processus de reproduction des plantes",
            "La transformation de l'énergie solaire en énergie chimique",
            "La décomposition des matières organiques",
            "L'absorption de l'eau et des nutriments par les racines"
        ],
        "answer": "La transformation de l'énergie solaire en énergie chimique",
        "duration": 10
    },
    {
        "question": "Quel est l'engrais naturel obtenu par la décomposition de matières organiques ?",
        "hint": "Cet engrais est produit à partir de matières naturelles en décomposition.",
        "options": [
            "Engrais minéral",
            "Engrais chimique",
            "Engrais organique",
            "Engrais foliaire"
        ],
        "answer": "Engrais organique",
        "duration": 10
    },
    # {
    #     "question": "Quelle est la technique qui consiste à cultiver plusieurs espèces végétales ensemble pour favoriser la biodiversité et limiter les maladies ?",
    #     "options": [
    #         "Culture en monoculture",
    #         "Culture en rotation",
    #         "Culture en association",
    #         "Culture en jachère"
    #     ],
    #     "answer": "Culture en association",
    #     "duration": 10
    # },
    # {
    #     "question": "Qu'est-ce que l'hydroponie ?",
    #     "options": [
    #         "Une technique de culture hors-sol utilisant un substrat nutritif liquide.",
    #         "Une méthode de culture biologique en plein champ.",
    #         "Un système d'irrigation traditionnel en agriculture.",
    #         "Une méthode de culture associant poissons et plantes."
    #     ],
    #     "answer": "Une technique de culture hors-sol utilisant un substrat nutritif liquide.",
    #     "duration": 10
    # },
    # {
    #     "question": "Quel est l'avantage de l'agriculture hydroponique en termes d'utilisation de l'eau ?",
    #     "options": [
    #         "Moins d'eau est utilisée par rapport à l'agriculture conventionnelle.",
    #         "Plus d'eau est nécessaire en raison de l'absence de sol.",
    #         "L'eau est complètement évitée dans ce type de culture.",
    #         "L'usage de l'eau est similaire à celui de l'agriculture traditionnelle."
    #     ],
    #     "answer": "Moins d'eau est utilisée par rapport à l'agriculture conventionnelle.",
    #     "duration": 10
    # },
    # {
    #     "question": "Quels sont les principaux nutriments fournis aux plantes dans l'hydroponie ?",
    #     "options": [
    #         "Azote, phosphore et potassium.",
    #         "Oxygène, azote et carbone.",
    #         "Calcium, magnésium et fer.",
    #         "Lumière, eau et chaleur."
    #     ],
    #     "answer": "Azote, phosphore et potassium.",
    #     "duration": 10
    # },
    # {
    #     "question": "Quel est l'impact environnemental de l'agriculture hydroponique ?",
    #     "options": [
    #         "Moins de consommation d'énergie et moins d'émissions de gaz à effet de serre.",
    #         "Une empreinte environnementale plus élevée par rapport à l'agriculture traditionnelle.",
    #         "Une dégradation du sol due à l'absence de culture en plein champ.",
    #         "Une utilisation excessive des ressources naturelles."
    #     ],
    #     "answer": "Moins de consommation d'énergie et moins d'émissions de gaz à effet de serre.",
    #     "duration": 10
    # }
]

# Supprimer toutes les questions de la collection
Question.objects.delete()
Challenge.objects.delete()
Score.objects.delete()
Participant.objects.delete()


# Insérer les questions dans la collection
print("Question")
for question_data in questions_list:
    question = Question(**question_data)
    question.created_by = "cf9e6aa4-d879-422d-b26d-8fac11cde5bf"
    question.save()
    time.sleep(1)
    print(question.id)


participants = [
    {
        "id": "6e01900e-4afd-48b7-95a1-513f0e50aeb4",
        "is_denied": False,
        "is_blocked": False
    },
    {
        "id": "6e01900e-4afd-48b7-95a1-513f0e50aeb5",
        "is_denied": False,
        "is_blocked": False
    },
    {
        "id": "6e01900e-4afd-48b7-95a1-513f0e50aeb6",
        "is_denied": False,
        "is_blocked": False
    }
]

print("Participants")
for participant_data in participants:
    participant = Participant(**participant_data)
    participant.save()
    time.sleep(1)
    print(participant.id)

print("Les questions ont été insérées avec succès.")
