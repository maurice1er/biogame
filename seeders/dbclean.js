const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');
const { Participant, Challenge, ChallengeResponse, Score, Question } = require('../models');

const dotenv = require('dotenv');
dotenv.config();


const { connectToDatabase,  } = require('../functions.js');

// env
const connectionString = process.env.MONGODB_URI;
connectToDatabase(connectionString);



async function clearDatabase() {
    try {
        await Question.deleteMany({});
        await Participant.deleteMany({});
        await Score.deleteMany({});
        await ChallengeResponse.deleteMany({});
        await Challenge.deleteMany({});
        console.log('Base de données nettoyée avec succès.');
    } catch (error) {
        console.error("Une erreur s'est produite lors de la suppression des documents :", error);
    } finally {
        mongoose.disconnect();
    }
}

  
// Appelez la fonction pour nettoyer la base de données
clearDatabase();
  