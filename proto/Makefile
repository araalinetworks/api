BUILD_DIR=../../build/proto
PROTOC_GEN_GO := $(GOPATH)/bin/protoc-gen-go
PROTOWRAP := $(GOPATH)/bin/protowrap
GOPATH=/home/ec2-user/src/

all: gen

doc: $(PROTOWRAP)
	echo "Generating documentation"
	PATH=${GOPATH}/bin:${PATH} protowrap --plugin=protoc-gen-doc=./protoc-gen-doc --doc_out=. --doc_opt=markdown,araali_api.md -I. ./araali_api_service.proto

$(PROTOC_GEN_GO): doc
	go get -u github.com/golang/protobuf/protoc-gen-go
	- go get -u google.golang.org/grpc
	cd $(GOPATH)/golang.org/x/net/ && git reset --hard 7fd8e65b642006927f6cec5cb4241df7f98a2210

$(PROTOWRAP):
	go get -u github.com/square/goprotowrap/cmd/protowrap

genpy:
	rm -rf pygen
	mkdir -p pygen
	python3 -m grpc_tools.protoc -I. --python_out=pygen --grpc_python_out=pygen ./*.proto

gen: $(PROTOC_GEN_GO) $(PROTOWRAP)
	PATH=${GOPATH}/bin:${PATH} protowrap --go_out=plugins=grpc:../ -I. ./*.proto

.PHONY: 
