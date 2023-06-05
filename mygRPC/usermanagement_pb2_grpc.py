# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import usermanagement_pb2 as usermanagement__pb2


class UserServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CheckUserExistence = channel.unary_unary(
            '/usermanagement.UserService/CheckUserExistence',
            request_serializer=usermanagement__pb2.UserExistenceRequest.SerializeToString,
            response_deserializer=usermanagement__pb2.UserExistenceResponse.FromString,
        )


class UserServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def CheckUserExistence(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_UserServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'CheckUserExistence': grpc.unary_unary_rpc_method_handler(
            servicer.CheckUserExistence,
            request_deserializer=usermanagement__pb2.UserExistenceRequest.FromString,
            response_serializer=usermanagement__pb2.UserExistenceResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'usermanagement.UserService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))

 # This class is part of an EXPERIMENTAL API.


class UserService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def CheckUserExistence(request,
                           target,
                           options=(),
                           channel_credentials=None,
                           call_credentials=None,
                           insecure=False,
                           compression=None,
                           wait_for_ready=None,
                           timeout=None,
                           metadata=None):
        return grpc.experimental.unary_unary(request, target, '/usermanagement.UserService/CheckUserExistence',
                                             usermanagement__pb2.UserExistenceRequest.SerializeToString,
                                             usermanagement__pb2.UserExistenceResponse.FromString,
                                             options, channel_credentials,
                                             insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
