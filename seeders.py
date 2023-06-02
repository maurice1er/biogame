import mongoengine
from models import Question, Challenge

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
        "answer": "Compostage"
    },
    {
        "question": "Qu'est-ce que la photosynthèse ?",
        "options": [
            "Le processus de reproduction des plantes",
            "La transformation de l'énergie solaire en énergie chimique",
            "La décomposition des matières organiques",
            "L'absorption de l'eau et des nutriments par les racines"
        ],
        "answer": "La transformation de l'énergie solaire en énergie chimique"
    },
    {
        "question": "Quel est l'engrais naturel obtenu par la décomposition de matières organiques ?",
        "options": [
            "Engrais minéral",
            "Engrais chimique",
            "Engrais organique",
            "Engrais foliaire"
        ],
        "answer": "Engrais organique"
    },
    {
        "question": "Quelle est la technique qui consiste à cultiver plusieurs espèces végétales ensemble pour favoriser la biodiversité et limiter les maladies ?",
        "options": [
            "Culture en monoculture",
            "Culture en rotation",
            "Culture en association",
            "Culture en jachère"
        ],
        "answer": "Culture en association"
    }
    # Ajoutez d'autres questions ici...
]

# Supprimer toutes les questions de la collection
Question.objects.delete()
Challenge.objects.delete()


# Insérer les questions dans la collection
for question_data in questions_list:
    question = Question(**question_data)
    question.created_by = "cf9e6aa4-d879-422d-b26d-8fac11cde5bf"
    question.save()
    print(question.id)
    print(" ")

print("Les questions ont été insérées avec succès.")
