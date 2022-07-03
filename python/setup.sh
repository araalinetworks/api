#!/bin/bash
python3 -m venv araalienv
source araalienv/bin/activate && python3 -m pip install --upgrade pip
source araalienv/bin/activate && pip install -r requirements.txt
python araalictl.py
sudo ./araalictl authorize -local
source araalienv/bin/activate && bash
