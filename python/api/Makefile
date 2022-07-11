GENDIR=src/araali

genpy: clean
	python3 -m grpc_tools.protoc -I../../proto --python_out=$(GENDIR) --grpc_python_out=$(GENDIR) ../../proto/*.proto
	sed -i -e 's/import araali_api_service_pb2/from . import araali_api_service_pb2/g' src/araali/araali_api_service_pb2_grpc.py

build: genpy
	python3 -m build

push:
	python3 -m twine upload dist/*

install: build
	python3 -m venv araaliapienv
	source araaliapienv/bin/activate && python3 -m pip install --upgrade pip
	source araaliapienv/bin/activate && pip install -r tests/requirements.txt
	source araaliapienv/bin/activate && pip install dist/*.tar.gz

test:
	-source araaliapienv/bin/activate && pytest

shell:
	source araaliapienv/bin/activate && bash
clean:
	rm -f dist/*
	rm -f $(GENDIR)/araali_api_service_pb2.py*
	rm -f $(GENDIR)/araali_api_service_pb2_grpc.py*
