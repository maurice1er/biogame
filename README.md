# biogame

The Biogame application is a websocket game server focused on agricultural quizzes, designed for participants to play in pairs. The server interacts with a gRPC server, which queries the "msuser" microservice responsible for user management. The gRPC client takes a user ID as a parameter and returns true if the user exists and false otherwise. This information is consumed by the websocket server, which executes further instructions based on the response.

The primary purpose of the Biogame application is to provide an interactive and engaging platform for users to participate in agriculture-themed quizzes. By leveraging gRPC and the "msuser" microservice, the application ensures that only existing users are allowed to join the game. This validation process enhances the security and integrity of the gameplay experience.

Upon successful verification of the user's existence, the websocket server proceeds with executing the appropriate game instructions and facilitating the quiz session between the paired participants. The participants can compete against each other, answer quiz questions, and receive real-time feedback on their performance.

Overall, the Biogame application provides an entertaining and educational environment for users to engage in agricultural quizzes, fostering knowledge sharing and friendly competition within the agriculture community.

## Clone project

```sh
git clone https://github.com/maurice1er/biogame.git
cd biogame
```

## Activate environment variable

To activate the virtual environment, run the following command:

```
python3 -m venv socket
source socket/bin/activate
```

## Set .env

Make sure to configure the following environment variables in your .env file:

```
TOP_PARTICPANT_REFRESH_TIME = 5
TOP_PARTICPANT_MESSAGE_WAIT_TIME = 6

MONGO_DB_NAME=quiz_db
MONGO_DB_HOST=localhost
MONGO_DB_PORT=27017
MONGO_DB_USERNAME=
MONGO_DB_PASSWORD=

WEBSOCKET_SERVER_HOST=localhost
WEBSOCKET_SERVER_PORT=8527
```

## Compile .proto file

```py
python -m grpc_tools.protoc -I mygRPC --python_out=mygRPC --grpc_python_out=mygRPC mygRPC/usermanagement.proto
```

## Run app

```shell
./init.sh
```
