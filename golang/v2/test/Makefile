all: gen build

build: gen
	CGO_ENABLED=0 GOOS=linux go build -o apitest.linux .
	CGO_ENABLED=0 GOOS=darwin go build -o apitest.darwin .

gen:
	cd ../../../proto && make

.PHONY: build gen
