all: gen run

run: gen
	PYTHONPATH=../../proto/araali/pygen python main.py

gen:
	cd ../../proto && make

.PHONY: build gen
