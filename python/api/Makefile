GENDIR=src/araali

genpy: clean
	python3 -m grpc_tools.protoc -I../../proto --python_out=$(GENDIR) --grpc_python_out=$(GENDIR) ../../proto/*.proto

build: genpy
	python3 -m build

push:
	python3 -m twine upload dist/*

clean:
	rm $(GENDIR)/araali_api_service_pb2.py
	rm $(GENDIR)/araali_api_service_pb2_grpc.py
