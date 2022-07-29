GENDIR=src/araali

# the default, full thing
all: genpy build install tox

# publish to pypi
push: venv
	source araaliapienv/bin/activate && python3 -m twine upload dist/*

# if you want to rerun tests to see if they succeed
test: venv
	-source araaliapienv/bin/activate && pytest -vs

# if you are fixing install
install: venv
	source araaliapienv/bin/activate && pip install dist/*.tar.gz

# if you are fixing build
checkbuild:
	@echo "*** checking if there are junk files in src ***"
	git -c color.status=false status src | grep src| wc -l | grep 0

# this is a dangerous command, but safe to do after you review the output of
# git -c color.status=false status src | grep src
prepbuild:
	git -c color.status=false status src | grep src| xargs rm -rf

build: venv checkbuild
	rm -f dist/*
	rm -f $(GENDIR)/bin/araalictl
	rm -f $(GENDIR)/bin/araalictl.*-amd64_*
	source araaliapienv/bin/activate && python3 -m build

# regenerating proto stubs
genpy: venv
	rm -f $(GENDIR)/araali_api_service_pb2.py*
	rm -f $(GENDIR)/araali_api_service_pb2_grpc.py*
	source araaliapienv/bin/activate && python3 -m grpc_tools.protoc -I../../proto --python_out=$(GENDIR) --grpc_python_out=$(GENDIR) ../../proto/*.proto
	sed -i -e 's/import araali_api_service_pb2/from . import araali_api_service_pb2/g' src/araali/araali_api_service_pb2_grpc.py

# isolated and fully controlled python environment
venv: araaliapienv/exists.h

# to keep a marker so we dont do this unnecessarily. Do "make clean" to start from scratch
araaliapienv/exists.h:
	python3 -m venv araaliapienv
	source araaliapienv/bin/activate && python3 -m pip install --upgrade pip
	source araaliapienv/bin/activate && pip install -r tests/requirements.txt
	touch araaliapienv/exists.h

# official clean blackbox tessting
tox:
	tox

# work in the python enviroment
shell:
	-source araaliapienv/bin/activate && bash

# get a new life, wash all karma
clean:
	rm -rf araaliapienv
	rm -rf .tox
