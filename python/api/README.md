# Araali API

This is a python library to expose access to Araali APIs

## Help
```
# setup a python3 virtualenv to run araali (one time)
cd ~/
python3 -m venv araaliapienv
source araaliapienv/bin/activate
pip install araali

# every other time (enter the environment you setup)
cd ~/
source araaliapienv/bin/activate
pip install --upgrade araali

# export your api token
export ARAALI_API_TOKEN="<your-token-here>"

# usage help - command line
python -m pydoc araali
python -m araali -h

# from your code
>>> import araali
>>> help(araali)
```
