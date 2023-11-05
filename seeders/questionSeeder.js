const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');
// const Question = require('../models/Question');
const { Question } = require("../models.js");


const dotenv = require('dotenv');
dotenv.config();


const { connectToDatabase,  } = require('../functions.js');

// env
const connectionString = process.env.MONGODB_URI;
connectToDatabase(connectionString);



const questions_list = [
    {
        "question": "Quel est le processus de conversion des matières organiques en compost riche en éléments nutritifs ?",
        "options": [
            "Fumigation",
            "Amendement",
            "Biodégradation",
            "Compostage"
        ],
        "answer": 3,
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
        "answer": 2,
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
        "answer": 3,
        "duration": 10
    },
    {
        "question": "Quelle technique hydroponique utilise un film mince d'eau en mouvement continu pour fournir des nutriments aux plantes sans utiliser de substrat de croissance ?",
        "options": [
            "NFT (Nutrient Film Technique)",
            "Aéroponie",
            "Culture en substrat",
            "Aquaponie"
        ],
        "answer": 1,
        "duration": 10
    },
    {
        "question": "Qu'est-ce que l'aéroponie en hydroponie ?",
        "hint": "Cette méthode utilise l'air pour livrer des nutriments aux plantes.",
        "options": [
            "Une technique de culture en plein champ",
            "Un système d'irrigation goutte à goutte",
            "Une méthode de culture en suspension dans l'air",
            "Un système de culture dans des bacs profonds"
        ],
        "answer": 2,
        "duration": 10
    },
    {
        "question": "Quel élément chimique est généralement fourni aux plantes sous forme de nitrate dans les solutions nutritives hydroponiques ?",
        "options": [
            "Azote (N)",
            "Phosphore (P)",
            "Potassium (K)",
            "Fer (Fe)"
        ],
        "answer": 1,
        "duration": 10
    },
    {
        "question": "Quel est le principal avantage de l'hydroponie par rapport à la culture traditionnelle dans le sol ?",
        "options": [
            "Meilleure absorption de la lumière",
            "Contrôle précis des nutriments et de l'eau",
            "Moins d'exposition aux maladies",
            "Meilleure aération des racines"
        ],
        "answer": 2,
        "duration": 10
    },
    {
        "question": "Quel est le substrat le plus couramment utilisé dans les systèmes hydroponiques ?",
        "options": [
            "Sable",
            "Terre de jardin",
            "Perlite",
            "Roches volcaniques"
        ],
        "answer": 3,
        "duration": 10
    },
    {
        "question": "Quelle est la méthode de culture hydroponique qui utilise des poissons ou d'autres organismes aquatiques pour fournir des nutriments aux plantes ?",
        "options": [
            "NFT (Nutrient Film Technique)",
            "Aéroponie",
            "Aquaponie",
            "Culture en substrat"
        ],
        "answer": 3,
        "duration": 10
    },
    {
        "question": "Quel paramètre est essentiel à surveiller de près dans un système hydroponique pour assurer un bon niveau d'oxygène aux racines des plantes ?",
        "options": [
            "Le pH de la solution nutritive",
            "La température de l'eau",
            "Le niveau d'humidité de l'air",
            "La concentration d'oxygène dans l'eau"
        ],
        "answer": 4,
        "duration": 10
    },
    {
        "question": "Quel type de lumière est le plus approprié pour la croissance des plantes dans un système hydroponique en intérieur ?",
        "options": [
            "Lumière rouge",
            "Lumière bleue",
            "Lumière jaune",
            "Lumière verte"
        ],
        "answer": 2,
        "duration": 10
    },
    {
        "question": "Quel est le rôle du potassium dans la croissance des plantes en hydroponie ?",
        "options": [
            "Stimulation de la floraison",
            "Renforcement de la structure cellulaire",
            "Absorption de l'azote",
            "Synthèse de la chlorophylle"
        ],
        "answer": 2,
        "duration": 10
    },
    {
        "question": "What is the chemical element represented by the symbol K in the periodic table of elements?",
        "options": [
            "Potassium",
            "Iron",
            "Calcium",
            "Sodium"
        ],
        "answer": 1,
        "language": "en",
        "duration": 18
    },
    {
        "question": "What is the main function of roots in a hydroponic system?",
        "options": [
            "Absorb water and nutrients",
            "Produce oxygen",
            "Store energy",
            "Protect the plant against diseases"
        ],
        "answer": 1,
        "language": "en",
        "duration": 15
    }
    
];

async function seedQuestions() {
    try {
      await Question.deleteMany({});
  
      const getRandomDate = () => {
        const start = new Date(2020, 0, 1);
        const end = new Date();
        return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
      };
  
      const questionsData = questions_list.map(question => {
        // const isEnglish =  === 'en'  Math.random() < 0.2; // 20% de chance d'être en anglais
        // const language = 
        return {
          _id: uuidv4(),
          question: question.question,
          hint: question.hint || '',
          options: question.options,
          answer: question.answer,
          language: question.language || 'fr',
          duration: question.duration || 10,
          created_by: 'cf9e6aa4-d879-422d-b26d-8fac11cde5bf',
          created_at: getRandomDate(),
          modified_at: getRandomDate(),
          is_enable: true,
        };
      });
  
      await Question.insertMany(questionsData);
  
      console.log('Questions générées avec succès.');
    } catch (error) {
      console.error('Une erreur s\'est produite lors de la génération des questions :', error);
    } finally {
      mongoose.disconnect();
    }
  }
  
seedQuestions();
