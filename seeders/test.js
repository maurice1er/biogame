const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');
const { Participant, Challenge, ChallengeResponse, Score, Question } = require('../models');

const dotenv = require('dotenv');
dotenv.config();


const { connectToDatabase,  } = require('../functions.js');

// env
const connectionString = process.env.MONGODB_URI;
connectToDatabase(connectionString);

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


const getRandomQuestions = async (count) => {
    try {
        const questions = await Question.aggregate([
            { $sample: { size: count } },
        ]);
        return questions;
    } catch (error) {
        console.error(error);
        throw error; // Rejeter la promesse en cas d'erreur
    }
};


const participantsData = [
    {
      _id: '4c22b5ab-0f9b-4458-8b63-b068c5abf6a0',
      username: 'Maurice',
      profile: '',
    },
    {
      _id: '5e6f7a8b-1c2d-3e4f-5a6b-7c8d9e0f1a2b',
      username: 'Nathalie',
      profile: '',
    },
  ];
  
const challengesData = [
    {
      _id: '90750a97-e3b5-449a-8473-bffb4e15f15e',
      challenger: '4c22b5ab-0f9b-4458-8b63-b068c5abf6a0',
      is_started: true,
      is_ended: false,
      challenger_score: 10,
      challenged_score: 0,
      questions: [
        {
          _id: '376902fd-6db2-4419-8248-49cc5a5ca4e2',
          question: 'Quel est le substrat le plus couramment utilisé dans les systèmes hydroponiques ?',
          hint: '',
          images: [],
          options: ['Sable', 'Terre de jardin', 'Perlite', 'Roches volcaniques'],
          answer: 3,
          language: 'fr',
          duration: 10,
          created_by: 'cf9e6aa4-d879-422d-b26d-8fac11cde5bf',
          created_at: new Date('2021-09-14T03:00:38.739Z'),
          modified_at: new Date('2022-09-02T02:33:46.686Z'),
          is_enable: true,
        },
      ],
      launched_date: new Date('2023-11-15T02:30:26.897Z'),
    },
  ];
  
const challengeResponsesData = [
    {
      _id: uuidv4(),
      challenge: '90750a97-e3b5-449a-8473-bffb4e15f15e',
      participant: '4c22b5ab-0f9b-4458-8b63-b068c5abf6a0',
      question: [
        {
          _id: '376902fd-6db2-4419-8248-49cc5a5ca4e2',
          question: 'Quel est le substrat le plus couramment utilisé dans les systèmes hydroponiques ?',
          hint: '',
          images: [],
          options: ['Sable', 'Terre de jardin', 'Perlite', 'Roches volcaniques'],
          answer: 3,
          language: 'fr',
          duration: 10,
          created_by: 'cf9e6aa4-d879-422d-b26d-8fac11cde5bf',
          created_at: new Date('2021-09-14T03:00:38.739Z'),
          modified_at: new Date('2022-09-02T02:33:46.686Z'),
          is_enable: true,
        },
      ],
      response: 3,
      is_correct: true,
    },
    // Ajoutez d'autres réponses au besoin
  ];
  
const scoresData = [
    {
      _id: 'c6a8c3bd-de33-44e0-b622-e67aa8de188b',
      challenge: '90750a97-e3b5-449a-8473-bffb4e15f15e',
      participant: '4c22b5ab-0f9b-4458-8b63-b068c5abf6a0',
      score: 10,
      is_challenger: true,
    },
    // Ajoutez d'autres scores au besoin
  ];
  
  
  
  
  
  async function seedData() {

  
      try {
          await Participant.insertMany(participantsData);
  
          for (const participant in participantsData) {

              console.log(participant);

              // challenge
              const _challenge = { ...challengesData[0] };
              _challenge._id = uuidv4();
              _challenge.challenger = participant._id;

              const questions = await getRandomQuestions(1);
              _challenge.questions = questions;
  
              // challengeResponses
              const _challengeResponses = { ...challengeResponsesData[0] };
              _challengeResponses._id = uuidv4();
              _challengeResponses.challenge = _challenge._id;
              _challengeResponses.participant = _challenge.challenger;
              _challengeResponses.question = _challenge.questions;
              _challengeResponses.response = 3;
              _challengeResponses.is_correct = _challenge.questions[0].answer === _challengeResponses.response;
              
              console.log(_challengeResponses._id);

              // score
              const _score = { ...scoresData[0] };
              _score._id = uuidv4();
              _score.challenge = _challenge._id;
              _score.participant = _challenge.challenger;
            //   _score.score = 10 ? _challengeResponses.is_correct : 0;
              _score: _challengeResponses.is_correct ? _challenge.challenger_score : _challenge.challenged_score,

  
              await Challenge.insertMany(_challenge);
              await ChallengeResponse.insertMany(_challengeResponses);
              await Score.insertMany(_score);

              await sleep(2000);  
  
          }
  
          console.log('Données semées avec succès.');
      } catch (error) {
          console.error("Une erreur s'est produite lors de l'ensemencement des données :", error);
      } finally {
          mongoose.disconnect();
      }
  
  }
  
seedData();

// Appelez la fonction pour nettoyer la base de données
//clearDatabase();
  