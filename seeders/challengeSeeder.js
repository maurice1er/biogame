const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');
const { Participant, Challenge } = require("../models.js");

const dotenv = require('dotenv');
dotenv.config();

const { connectToDatabase } = require('../functions.js');

// env
const connectionString = process.env.MONGODB_URI;
connectToDatabase(connectionString);

const participantsData = [
  { _id: '9a655a4a-8a5d-4c0a-a21e-c7481b178efc', username: 'Participant1', profile: '' },
  { _id: 'f5e3b8cd-33d6-4d43-8059-6b7f2d5cc9c7', username: 'Participant2', profile: '' },
  { _id: '0c3f6f87-00f2-407b-90e2-ff9b0a6db4a8', username: 'Participant3', profile: '' },
  { _id: '689081a2-e23a-4e0f-9fcd-3b70c89c683e', username: 'Participant4', profile: '' },
  { _id: '6ee14db4-825a-492d-a1b1-92f3a92a373b', username: 'Participant5', profile: '' },
];

async function seedParticipantsAndChallenges() {
  try {
    // Delete existing participants and challenges
    await Participant.deleteMany({});
    await Challenge.deleteMany({});

    // Insert participants
    await Participant.insertMany(participantsData);

    // Fetch all participants
    const participants = await Participant.find();

    // Generate challenges for each participant
    for (const participant of participants) {
      const challengesData = Array.from({ length: 3 }, (_, index) => {
        return {
          _id: uuidv4(),
          challenger: participant._id,
          challenged: participants[(index + 1) % participants.length]._id,
          is_started: true,
          is_ended: false,
          launched_date: new Date(),
          questions: [], // Add questions data if needed
        };
      });

      // Insert challenges for the participant
      await Challenge.insertMany(challengesData);
    }

    console.log('Participants et challenges générés avec succès.');
  } catch (error) {
    console.error('Une erreur s\'est produite lors de la génération des participants et des challenges :', error);
  } finally {
    mongoose.disconnect();
  }
}

seedParticipantsAndChallenges();
