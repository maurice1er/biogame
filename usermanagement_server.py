import grpc

from grpc import RpcError

import requests
from concurrent import futures
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from google.protobuf.timestamp_pb2 import Timestamp

from mygRPC import usermanagement_pb2
from mygRPC import usermanagement_pb2_grpc


class UserService(usermanagement_pb2_grpc.UserServiceServicer):
    def CheckUserExistence(self, request, context):
        # Logique de vérification de l'existence de l'utilisateur
        participant_id = request.participant_id

        try:
            # Effectuer la vérification dans votre microservice "msuser"
            msuser_url = f"http://localhost:1105/api/users/id/{participant_id}"
            response = requests.get(msuser_url)

            user_exists = response.status_code == 200

            return usermanagement_pb2.UserExistenceResponse(user_exists=user_exists)
        # except requests.exceptions.RequestException as e:
        #     print('Request Exception')
        except:
            return usermanagement_pb2.UserExistenceResponse(user_exists=False)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    usermanagement_pb2_grpc.add_UserServiceServicer_to_server(
        UserService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC Server started --> [::]:50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
