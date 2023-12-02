const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');

const { Participant, Question, Score, Challenge, ChallengeResponse } = require("./models.js");



const connectToDatabase = async (connectionString) => {
    try {
        // Use async/await to wait for the connection to be established
        await mongoose.connect(connectionString, {
            useNewUrlParser: true,
            // useUnifiedTopology: true
        });

        console.log('Connected to MongoDB successfully');
    } catch (error) {
        console.error('Error connecting to MongoDB:', error);
        process.exit(1); // Exit the application if the connection fails
    }
}


const updateTopParticipants = async () => {
    try {
        // Effectuer la jointure et le groupage
        const results = await Score.aggregate([
            {
                $lookup: {
                    from: 'participants',
                    localField: 'participant',
                    foreignField: '_id',
                    as: 'participant_info',
                },
            },
            {
                $group: {
                    _id: '$participant',
                    totalScore: { $sum: '$score' },
                    numberOfChallenges: { $sum: 1 }, // Ajoutez cette ligne pour compter le nombre de challenges par participant
                    username: { $first: '$participant_info.username' },
                    profile: { $first: '$participant_info.profile' },
                },
            },
        ]);

        const topParticipants = results.map(result => ({
            id: result._id,
            score: result.totalScore,
            numberOfChallenges: result.numberOfChallenges,
            username: result.username[0],
            profile: result.profile[0],
        }));

        return topParticipants.sort((a, b) => b.score - a.score);
    } catch (error) {
        console.error("Une erreur s'est produite :", error);
        throw error;
    }
}



const getRandomQuestions = async (lang = 'fr', size = 1) => {
    try {
        // Utilisation de l'agrégation avec $match pour filtrer par langue "fr" et $sample pour obtenir deux documents aléatoires
        const randomQuestions = await Question.aggregate([
            { $match: { language: lang } }, // Filtrer par langue "fr"
            { $sample: { size: size } } //
        ]);

        return randomQuestions;
    } catch (error) {
        // console.error("Erreur lors de la récupération des questions aléatoires", error);
        return [];
    }
}


const insertChallengeResponse = async (challengeId, participantId, questionId, response, isCorrect) => {
    try {
        // Recherche du challenge par son ID
        const challenge = await Challenge.findById(challengeId);
        if (!challenge) {
            console.log("Challenge not found");
            return;
        }

        // Recherche du participant par son ID
        const participant = await Participant.findById(participantId);
        if (!participant) {
            console.log("Participant not found");
            return;
        }

        // Recherche de la question par son ID
        const question = await Question.findById(questionId);
        if (!question) {
            console.log("Question not found");
            return null;
        }

        // Création de la réponse au challenge
        const challengeResponse = new ChallengeResponse({
            challenge: challenge._id,
            participant: participant._id,
            question: question,
            response: response ? response.answer : null,
            is_correct: isCorrect,
        });

        // Enregistrement de la réponse au challenge
        await challengeResponse.save();
        // console.log("Challenge response saved successfully");
    } catch (error) {
        // console.error("Error inserting into ChallengeResponse collection:", error);
        return null;
    }
}


const decodeJwtToken = async (tokenHeader, jwtSecret) => {
    // Extrait le token JWT de l'en-tête
    // console.log(tokenHeader);

    const token = tokenHeader.replace('Bearer ', '');

    try {
        // Décoder le token JWT
        const decoded = jwt.verify(token, jwtSecret);

        // Obtenez la date actuelle en secondes (divisée par 1000 pour obtenir le temps en secondes)
        const currentTimestamp = Math.floor(Date.now() / 1000);

        // Vérifiez si la date d'expiration (exp) du token est supérieure à la date actuelle
        if (decoded.exp > currentTimestamp) {
            // Le token est valide, vous pouvez accéder aux informations du token
            return decoded;
        } else {
            // Le token JWT a expiré
            console.error('Token JWT expiré.');
            return null;
        }

    } catch (error) {
        // Le token JWT est invalide
        console.error('Token JWT invalide :', error.message);
        return null;
    }
}


const updateAvailableChallenges = async (challengerId) => {
    try {
        // Effectuer la jointure et filtrer les challenges selon les critères
        const challenges = await Challenge.aggregate([
            {
                $match: {
                    is_ended: false,
                    accepted_date: { $exists: false }, // Assurez-vous que la date d'acceptation existe
                    challenger: { $ne: challengerId }, // Exclure les challenges créés par le challenger lui-même
                }
            },
            {
                $lookup: {
                    from: 'participants',
                    localField: 'challenger',
                    foreignField: '_id',
                    as: 'challenger_info',
                },
            }
        ]);

        // Obtenez les informations du top participant
        const topParticipants = await updateTopParticipants();



        // Attribuer le classement et le score aux challenges
        const challengesWithRankAndScore = challenges.map(challenge => {
            const challengerId = challenge.challenger_info[0]._id.toString();
            const participantInfo = topParticipants.find(participant => participant.id === challengerId);

            const rankIndex = topParticipants.findIndex(participant => participant.id === challengerId);
            const totalDuration = challenge.questions.reduce((sum, question) => sum + question.duration, 0);


            return {
                challengeId: challenge._id,
                challenger: participantInfo,
                rank: rankIndex !== -1 ? rankIndex + 1 : -1,
                totalDuration: totalDuration, 
                // Ajoutez d'autres champs formatés ici
            };
        });

        return challengesWithRankAndScore;
    } catch (error) {
        console.error("Une erreur s'est produite :", error);
        throw error;
    }
};


module.exports = {
    connectToDatabase,
    updateTopParticipants,
    getRandomQuestions,
    insertChallengeResponse,
    decodeJwtToken,
    updateAvailableChallenges
};

