import grpc
import os

from grpc import RpcError

import requests
from concurrent import futures
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from google.protobuf.timestamp_pb2 import Timestamp

from user_gRPC import usermanagement_pb2
from user_gRPC import usermanagement_pb2_grpc


ms_user_host = os.getenv('MS_USER_HOST')


class UserService(usermanagement_pb2_grpc.UserServiceServicer):
    def CheckUserExistence(self, request, context):
        # Logique de vérification de l'existence de l'utilisateur
        participant_id = request.participant_id
        print(participant_id)
        print(" -+-+-> 1 ")

        ms_user_host = os.getenv('MS_USER_HOST')
        ms_user_url = f"{ms_user_host}/{participant_id}"
        print(ms_user_url)
        print(" -+-+-> 2 ")

        try:
            # Effectuer la vérification dans votre microservice "msuser"
            response = requests.get(ms_user_url)

            print(" ")
            print(response)
            print(" -+-+-> 3 ")
            print(" ")

            if response.status_code == 200:
                response_json = response.json()
                user_username = response_json.get("username", "")
                user_picture = response_json.get("imageUrl", "")

                print(" -+-+-> 4 ")
                print(usermanagement_pb2.UserExistenceResponse(
                    user_exists=True, username=user_username, picture=user_picture))
                return usermanagement_pb2.UserExistenceResponse(user_exists=True, username=user_username, picture=user_picture)
            else:
                print(" -+-+-> 5 ")
                return usermanagement_pb2.UserExistenceResponse(user_exists=False)

        except Exception as ex:
            print(" -+-+-> erreur ")
            print(ex)
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
    print(f"ms user host = {ms_user_host}")
    serve()
