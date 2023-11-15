const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');


// Définition du schéma MongoDB pour le modèle de question
const questionSchema = new mongoose.Schema({
    _id: { type: String, default: uuidv4, primary_key: true },
    // id: { type: String, default: uuidv4, primary_key: true },
    question: { type: String, required: true },
    hint: String,
    images: [String],
    options: [String],
    answer: { type: Number, required: true },
    language: { type: String, enum: ['fr', 'en'], default: 'fr' },
    duration: { type: Number, default: 10 },
    created_by: { type: String, required: true },
    created_at: { type: Date, default: Date.now },
    modified_at: { type: Date, default: Date.now },
    is_enable: { type: Boolean, default: true },
    category: { type: String },
    tags: [String],
    difficulty: { type: Number, default: 1 }
});

// Création du modèle de question
const Question = mongoose.model('Question', questionSchema);

// Définition du schéma MongoDB pour le modèle de participant
const participantSchema = new mongoose.Schema({
    _id: { type: String, required: true, unique: true },
    username: String,
    profile: String
}, { collection: 'participants', autoIndex: false });

const Participant = mongoose.model('Participant', participantSchema);





// Définition du schéma MongoDB pour le modèle de challenge
const challengeSchema = new mongoose.Schema({
    _id: { type: String, default: uuidv4, primary_key: true },
    challenger: { type: String, ref: 'Participant' },
    challenged: { type: String, ref: 'Participant' },
    winner: { type: String, ref: 'Participant' },
    is_started: { type: Boolean, default: true },
    is_ended: { type: Boolean, default: false },
    launched_date: { type: Date, default: Date.now },
    accepted_date: Date,
    ended_date: Date,
    challenger_score: { type: Number, default: 0 },
    challenged_score: { type: Number, default: 0 },
    questions: [questionSchema],
});

// Création du modèle de challenge
const Challenge = mongoose.model('Challenge', challengeSchema);



// Définition du schéma MongoDB pour le modèle de score
const scoreSchema = {
    _id: { type: String, default: uuidv4, primary_key: true },
    // id: String,
    challenge: String,
    participant: String,
    score: { type: Number, default: 0, },
    is_challenger: Boolean
};

// Création du modèle de score
const Score = mongoose.model('Score', scoreSchema);



// Définition du schéma MongoDB pour le modèle de réponse de challenge
const challengeResponseSchema = new mongoose.Schema({
    _id: { type: String, default: uuidv4, primary_key: true },
    challenge: { type: String, },
    participant: { type: String, },
    question: [questionSchema],
    response: Number,
    is_correct: { type: Boolean, default: false },
});

// Création du modèle de réponse de challenge
const ChallengeResponse = mongoose.model('ChallengeResponse', challengeResponseSchema);


// Export des modèles
module.exports = {
    Question,
    Participant,
    Challenge,
    Score,
    ChallengeResponse
};
