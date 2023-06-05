source socket/bin/activate 


python -m grpc_tools.protoc -I mygRPC --python_out=mygRPC --grpc_python_out=mygRPC mygRPC/usermanagement.proto
