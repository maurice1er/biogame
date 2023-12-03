const WebSocket = require('ws');
const http = require('http');
const Consul = require('consul');

// const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');
dotenv.config();

// const mongoose = require('mongoose');

const { connectToDatabase, updateTopParticipants, getRandomQuestions, insertChallengeResponse, decodeJwtToken, updateAvailableChallenges } = require('./functions');

// const { v4: uuidv4 } = require('uuid');
const { Participant, Question, Score, Challenge, ChallengeResponse } = require("./models.js");

console.log(process.env.NODE_ENV);
console.log(process.env.MONGODB_URI);
console.log(process.env.JWT_TOKEN_SECRET);

console.log(process.env.CONSUL_IP);
console.log(process.env.CONSUL_PORT);


// const server = http.createServer((req, res) => {
//     res.writeHead(200, { 'Content-Type': 'text/plain' });
//     res.end('Serveur WebSocket en cours d\'exécution');
// });

const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'application/json' });

    const jsonResponse = {
        message: 'Serveur WebSocket en cours d\'exécution',
        status: 'OK'
    };
    res.end(JSON.stringify(jsonResponse));
});

// env
const connectionString = process.env.MONGODB_URI;
const port = process.env.PORT || 8080;
const jwtTokenSecret = process.env.JWT_TOKEN_SECRET;

const randomQuestions = Number(process.env.RANDOM_QUESTIONS) || 1;
const questionDefaultLanguague = process.env.QUESTION_DEFAULT_LANGUAGUE || 'fr';

const consulIp = process.env.CONSUL_IP || "localhost";
const consulPort = Number(process.env.CONSUL_PORT) || 8500;



// Call the connectToDatabase function to establish the MongoDB connection
connectToDatabase(connectionString);



const wss = new WebSocket.Server({ noServer: true });



// socket

wss.on('topParticipants', async (ws, req) => {
    console.log('Nouvelle connexion WebSocket établie --> top-participants.');

    const tokenHeader = req.headers.authorization;

    // Vérifiez si l'en-tête Authorization existe
    if (!tokenHeader) {
        console.error('En-tête d\'autorisation manquant. La connexion WebSocket est fermée.');
        ws.close(1008, 'Unauthorized'); // Code 1008 pour non autorisé
        return;
    }
    let userInfo = await decodeJwtToken(tokenHeader, jwtTokenSecret);
    if (userInfo == null) {
        ws.close(1008, 'Unauthorized'); // Code 1008 pour non autorisé
        return;
    };


    if (!userInfo.permissions || (!userInfo.permissions.includes("canListTopParticipants") && !userInfo.permissions.includes("*"))) {
        console.log("pas de permission");
        ws.close(1003, 'Forbidden'); // Code 1003 pour interdit
        return;
    }

    // let participantId = userInfo.sub;
    // let participantUsername = userInfo.username;
    // let participantProfile = userInfo.profile;
    // console.log(participantId);

    // Fonction pour envoyer les meilleurs participants aux clients
    const sendTopParticipants = async () => {
        try {
            const topParticipants = await updateTopParticipants(); // topParticipants.sort((a, b) => b['score'].compareTo(a['score']));

            ws.send(JSON.stringify({ participants: topParticipants }));
        } catch (error) {
            console.error("Erreur lors de la récupération des meilleurs participants :", error);
        }
    };

    setInterval(sendTopParticipants, 5000);

});

wss.on('clean', async (ws) => {
    console.log('Nouvelle connexion WebSocket établie.');
    // Supprimez tous les documents de la collection "participants"
    async function clean() {
        try {
            await Participant.deleteMany({});
            await Challenge.deleteMany({});
            await Score.deleteMany({});
            await ChallengeResponse.deleteMany({});
            console.log("Tous les participants ont été supprimés.");
        } catch (error) {
            console.error("Une erreur s'est produite lors de la suppression des participants :", error);
        }
    }

    // Appelez la fonction pour supprimer tous les participants
    clean();

    ws.close();
});


wss.on('challenges', async (ws, req) => {
    console.log('Nouvelle connexion WebSocket établie.');

    const tokenHeader = req.headers.authorization;

    // Vérifiez si l'en-tête Authorization existe
    if (!tokenHeader) {
        console.error('En-tête d\'autorisation manquant. La connexion WebSocket est fermée.');
        ws.close(1008, 'Unauthorized'); // Code 1008 pour non autorisé
        return;
    }
    let userInfo = await decodeJwtToken(tokenHeader, jwtTokenSecret);
    if (userInfo == null) {
        ws.close(1008, 'Unauthorized'); // Code 1008 pour non autorisé
        return;
    };

    if (!userInfo.permissions || (!userInfo.permissions.includes("canListChallenges") && !userInfo.permissions.includes("*"))) {
        console.log("pas de permission");
        ws.close(1003, 'Forbidden'); // Code 1003 pour interdit
        return;
    }

    let participantId = userInfo.id;

    ws.on('close', () => {
        console.log('Connexion WebSocket fermée.');
        return;
        // Ajoutez ici le code pour fermer la connexion à la base de données MongoDB si nécessaire
        // Par exemple : mongoose.connection.close();
    });

    // Fonction pour envoyer les meilleurs participants aux clients
    const sendAvailableChallenges = async () => {
        try {
            const challenges = await updateAvailableChallenges(participantId);

            console.log(challenges);

            ws.send(JSON.stringify({ challenges: challenges }));
        } catch (error) {
            // Gérez les erreurs ici, par exemple, fermez la connexion WebSocket en cas d'erreur
            console.error('Erreur lors de l\'envoi des challenges:', error);
            ws.close(1011, 'Internal Error'); // Code 1011 pour erreur interne
        }
    };

    setInterval(sendAvailableChallenges, 5000);

});





wss.on('start', async (ws, req) => {
    console.log('Nouvelle connexion WebSocket établie.');

    const tokenHeader = req.headers.authorization;

    // Vérifiez si l'en-tête Authorization existe
    if (!tokenHeader) {
        console.error('En-tête d\'autorisation manquant. La connexion WebSocket est fermée.');
        ws.close(1008, 'Unauthorized'); // Code 1008 pour non autorisé
        return;
    }
    let userInfo = await decodeJwtToken(tokenHeader, jwtTokenSecret);
    if (userInfo == null) {
        ws.close(1008, 'Unauthorized'); // Code 1008 pour non autorisé
        return;
    };


    if (!userInfo.permissions || (!userInfo.permissions.includes("canStartChallenge") && !userInfo.permissions.includes("*"))) {
        console.log("pas de permission");
        ws.close(1003, 'Forbidden'); // Code 1003 pour interdit
        return;
    }


    let participantId = userInfo.id;
    let participantUsername = userInfo.username;
    let participantProfile = userInfo.profile;
    // console.log(participantId);



    // Initialisez l'index de la question actuelle à zéro
    let currentQuestionIndex = 0;

    // Récupérez toutes les questions depuis la base de données
    const questions = await getRandomQuestions(language = questionDefaultLanguague, size = randomQuestions);


    if (questions.length < 1) {
        console.error("Liste de question vide");
        ws.close();
    }
    // Question.find().exec();


    //----->

    const challenger = await Participant.findOne({ _id: participantId });

    if (!challenger) {
        const newParticipant = new Participant({
            _id: participantId,
            username: participantUsername,
            profile: participantProfile
        });

        await newParticipant.save();
    } else {
        await Participant.findOneAndUpdate(
            { _id: participantId },
            { $set: { username: participantUsername, profile: participantProfile } },
            { new: true } // Cette option renvoie le document mis à jour au lieu de l'original
        );
    }

    // Création du défi
    const challenge = new Challenge({
        challenger: participantId,
        is_started: true,
        questions: questions
    });
    const challengeSaved = await challenge.save();


    // Créez un nouvel objet Score
    const score = new Score({
        challenge: challengeSaved._id,
        participant: participantId,
        is_challenger: true,
    });
    score.save();

    // }



    // } catch (error) {
    //     console.error("Une erreur s'est produite lors de la création du défi :", error);
    //     throw error;
    // }

    //-----> 


    // try {

    // Fonction pour envoyer une question au participant
    function sendQuestion(ws, index) {
        const question = questions[index];
        if (question) {
            ws.send(JSON.stringify({ question: question })); // question au format JSON
        }
    }

    // Commencez par envoyer la première question
    sendQuestion(ws, currentQuestionIndex);


    // } catch (error) {
    //     console.error("Une erreur s'est produite lors l'envoi des questions :", error);
    //     throw error;
    // }



    // Gestion des messages entrants
    ws.on('message', async (message) => {
        try {
            // Traitement des réponses du participant ici...
            // console.log(JSON.parse(message));

            // Convertissez la réponse du participant en un objet JavaScript
            const participantResponse = JSON.parse(message);

            // Obtenez la question actuelle
            const currentQuestion = questions[currentQuestionIndex];
            // console.log(currentQuestion.answer + " = " + participantResponse.answer);

            if (currentQuestion && participantResponse && participantResponse.answer !== undefined) {
                // Vérifiez si la réponse du participant correspond à la réponse correcte de la question
                let isCorrect = participantResponse && participantResponse.answer === currentQuestion.answer;
                insertChallengeResponse(challengeSaved._id, participantId, currentQuestion._id, participantResponse, isCorrect);

                if (isCorrect) {
                    // La réponse est correcte, vous pouvez prendre des mesures ici

                    if (challengeSaved.challenger && challengeSaved.challenger === participantId) {
                        // Le participant est le challenger, augmentez son score de 10 points
                        challengeSaved.challenger_score += 10;
                        await challengeSaved.save();

                        score.score += 10;
                        await score.save();

                        console.log('Réponse correcte !');
                    }

                } else {
                    // La réponse est incorrecte, vous pouvez prendre des mesures ici
                    console.log('Réponse incorrecte.');
                }

                // Passez à la question suivante
                currentQuestionIndex++;


                if (currentQuestionIndex >= questions.length) {

                    ws.send(JSON.stringify({ end: { status: true, challengeId: challengeSaved._id } }));
                    ws.close();
                }
                // Vérifiez si toutes les questions ont été envoyées
                sendQuestion(ws, currentQuestionIndex);

            } else {
                // participantResponse n'est pas défini ou ne contient pas la propriété 'answer'
                console.error("Réponse du participant invalide.");
                ws.close();
            }
        } catch (error) {
            console.error("Erreur lors du traitement du message WebSocket :", error);
            ws.close();
        }
    });

    ws.on('close', () => {
        console.log('Connexion WebSocket fermée.');
    });
});


wss.on('accept', async (ws, req) => {
    console.log('Nouvelle connexion WebSocket établie: accept-challenge');

    const tokenHeader = req.headers.authorization;

    // Vérifiez si l'en-tête Authorization existe
    if (!tokenHeader) {
        console.error('En-tête d\'autorisation manquant. La connexion WebSocket est fermée.');
        ws.close(1008, 'Unauthorized'); // Code 1008 pour non autorisé
        return;
    }
    let userInfo = await decodeJwtToken(tokenHeader, jwtTokenSecret);
    if (userInfo == null) {
        ws.close(1008, 'Unauthorized'); // Code 1008 pour non autorisé
        return;
    };

    if (!userInfo.permissions || (!userInfo.permissions.includes("canAcceptChallenge") && !userInfo.permissions.includes("*"))) {
        console.log("pas de permission");
        ws.close(1003, 'Forbidden'); // Code 1003 pour interdit
        return;
    }

    let participantId = userInfo.id;
    let participantUsername = userInfo.username;
    let participantProfile = userInfo.profile;
    // console.log(participantId);




    // Initialisez l'index de la question actuelle à zéro
    let currentQuestionIndex = 0;
    let questions = [];


    // si le challengé n'existe pas dans Participant le crée sinon le mettre à jour
    const challenged = await Participant.findOne({ _id: participantId });

    if (!challenged) {
        const newParticipant = new Participant({
            _id: participantId,
            username: participantUsername,
            profile: participantProfile
        });

        await newParticipant.save();
    } else {
        await Participant.findOneAndUpdate(
            { _id: participantId },
            { $set: { username: participantUsername, profile: participantProfile } },
            { new: true } // Cette option renvoie le document mis à jour au lieu de l'original
        );
    }


    // Gestion des messages entrants
    ws.on('message', async (message) => {
        try {
            // Traitement des messages du participant ici...
            const request = JSON.parse(message);

            // console.log(request);

            if (request.challengeId) {

                // Récupérez l'ID du challenge fourni par le participant
                const challengeId = request.challengeId;

                // Recherchez le challenge en fonction de son ID, en excluant les challenges créés par le participant
                const challenge = await Challenge.findOne({ _id: challengeId, challenger: { $ne: participantId } });

                if (challenge) {
                    challenge.challenged = participantId;
                    challenge.accepted_date = Date.now();
                    await challenge.save();


                    // Si le challenge existe, récupérez les questions associées
                    questions = challenge.questions;

                    // Fonction pour envoyer une question au participant
                    function sendQuestion(ws, index) {
                        const question = questions[index];
                        if (question) {
                            // ws.send(JSON.stringify(question)); // question au format JSON
                            ws.send(JSON.stringify({ question: question })); // question au format JSON
                        }
                    }
                    // Commencez par envoyer la première question
                    sendQuestion(ws, currentQuestionIndex);


                    // Gestion des messages entrants pour les réponses du participant
                    ws.on('message', async (message) => {
                        // Traitement des réponses du participant ici...
                        // console.log(JSON.parse(message));

                        // Convertissez la réponse du participant en un objet JavaScript
                        const participantResponse = JSON.parse(message);

                        // Obtenez la question actuelle
                        const currentQuestion = questions[currentQuestionIndex];

                        // Vérifiez si la réponse du participant correspond à la réponse correcte de la question
                        let isCorrect = participantResponse.answer === currentQuestion.answer;
                        insertChallengeResponse(challenge._id, participantId, currentQuestion._id, participantResponse, isCorrect);

                        if (isCorrect) {
                            // La réponse est correcte, vous pouvez prendre des mesures ici

                            // if (challenge.challenged && challenge.challenged === participantId) {
                            // Le participant est le challenged, augmentez son score de 10 points
                            challenge.challenged_score += 10;
                            await challenge.save();

                            // Mettez à jour le score du participant
                            const score = new Score({
                                challenge: challenge._id,
                                participant: participantId,
                                is_challenger: false,
                            });
                            score.score += 10;
                            await score.save();

                            console.log('Réponse correcte !');
                            // }
                        } else {
                            // La réponse est incorrecte, vous pouvez prendre des mesures ici
                            console.log('Réponse incorrecte.');
                        }

                        // Passez à la question suivante
                        currentQuestionIndex++;

                        // sendQuestion(ws, currentQuestionIndex);

                        if (challenge.challenger_score > challenge.challenged_score) {
                            challenge.winner = challenge.challenger;
                        } else {
                            challenge.winner = challenge.challenged;
                        }
                        await challenge.save();

                        if (currentQuestionIndex >= questions.length) {
                            // ended
                            challenge.is_ended = true;
                            await challenge.save();

                            ws.send(JSON.stringify({ end: { status: true, challengeId: challenge._id } }));
                            ws.close();
                        }
                        // Vérifiez si toutes les questions ont été envoyées
                        sendQuestion(ws, currentQuestionIndex);

                        // // Vérifiez si toutes les questions ont été envoyées
                        // if (currentQuestionIndex < questions.length) {
                        //     sendQuestion(ws, currentQuestionIndex);
                        // } else {


                        // // Toutes les questions ont été envoyées, vous pouvez informer le participant que le jeu est terminé.
                        // ws.send(JSON.stringify({ message: 'Le jeu est terminé. Merci de jouer !' }));
                        // ws.close();

                        // }
                    });
                } else {
                    // Si le challenge n'existe pas, envoyez un message d'erreur
                    ws.send(JSON.stringify({ error: 'Challenge not found' }));
                }
            }

        } catch (error) {
            console.error('Erreur de traitement du message :', error);
        }
    });
});



// merge path 

server.on('upgrade', (request, socket, head) => {

    if (request.url === '/top-participants') {
        wss.handleUpgrade(request, socket, head, (ws) => {
            wss.emit('topParticipants', ws, request);
        });
    } else if (request.url === '/available-challenges') {
        wss.handleUpgrade(request, socket, head, (ws) => {
            wss.emit('challenges', ws, request);
        });
    } else if (request.url === '/start-challenge') {
        wss.handleUpgrade(request, socket, head, (ws) => {
            wss.emit('start', ws, request);
        });
    } else if (request.url === '/accept-challenge') {
        wss.handleUpgrade(request, socket, head, (ws) => {
            wss.emit('accept', ws, request);
        });
    } else if (request.url === '/clean') {
        wss.handleUpgrade(request, socket, head, (ws) => {
            wss.emit('clean', ws, request);
        });
    } else {
        socket.destroy();
    }

});


// Register service with Consul
// const consulClient = new Consul(); 
const consulClient = new Consul({ host: consulIp, port: consulPort });
consulClient.agent.service.register({
    name: 'ChallengeWs',
    address: 'localhost',
    port: 3000,
    tags: ['backend', 'websocket'],
    checks: [{
        http: `http://websocket:3000/health`,
        interval: '5s'
    }]
});


// run server

server.listen(3000, () => {
    console.log(`Serveur WebSocket écoutant sur le port ${port}`);
});




// "canListParticipants"
// "canListTopParticipants"
// "canListChallenges"
// "canStartChallenge"
// "canAcceptChallenge"
