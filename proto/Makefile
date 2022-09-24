BUILD_DIR=../../build/proto
PROTOC_GEN_GO := $(GOPATH)/bin/protoc-gen-go
PROTOC_GEN_DOC := $(GOPATH)/bin/protoc-gen-doc
PROTOWRAP := $(GOPATH)/bin/protowrap

all: gen

$(PROTOC_GEN_GO):
	go get -u github.com/golang/protobuf/protoc-gen-go
	- go get -u google.golang.org/grpc
	cd $(GOPATH)/golang.org/x/net/ && git reset --hard 7fd8e65b642006927f6cec5cb4241df7f98a2210

$(PROTOWRAP):
	go get -u github.com/square/goprotowrap/cmd/protowrap

$(PROTOC_GEN_DOC):
	cd ../golang && go install github.com/pseudomuto/protoc-gen-doc/cmd/protoc-gen-doc

doc: $(PROTOC_GEN_GO) $(PROTOC_GEN_DOC) $(PROTOWRAP)
	echo "Generating documentation"
	PATH=${GOPATH}/bin:${PATH} protoc -I . --swagger_out . \
        --swagger_opt logtostderr=true \
        --swagger_opt grpc_api_configuration=./araali_api_service.config.yaml \
        araali_api_service.proto
	PATH=${GOPATH}/bin:${PATH} protowrap --doc_out=. --doc_opt=markdown,araali_api.md -I. ./araali_api_service.proto

gen: $(PROTOC_GEN_GO) $(PROTOWRAP)
	PATH=${GOPATH}/bin:${PATH} protowrap --go_out=plugins=grpc:.. -I. ./*.proto

.PHONY:
