module araali/third_party/api/golang/v2/test

go 1.14

require (
	araali.proto v0.0.0
	github.com/araalinetworks/araali/third_party/api/golang/v2/araalictl v0.0.0
	google.golang.org/grpc v1.47.0 // indirect
	google.golang.org/protobuf v1.28.0
)

replace araali.proto v0.0.0 => ../../../proto/araali

replace github.com/araalinetworks/araali/third_party/api/golang/v2/araalictl v0.0.0 => ../araalictl
