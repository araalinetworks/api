#!/bin/bash
git pull
python3 -m venv araali
source araali/bin/activate && python3 -m pip install --upgrade pip
source araali/bin/activate && pip install -r requirements.txt
python araalictl.py
sudo ./araalictl authorize -local
source araali/bin/activate && jupyter notebook
