module github.com/araalinetworks/api/golang/v2/araalictl

go 1.14

require (
	araali.proto v0.0.0
	google.golang.org/grpc v1.47.0
	google.golang.org/protobuf v1.28.0 // indirect
)

replace araali.proto => ../../../proto/araali
