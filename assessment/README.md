# Getting Started
```
mkdir araalinetworks
cd araalinetworks
git clone https://github.com/araalinetworks/api.git
cd api/python

# install/upgrade
python araalictl.py

# to authorize your copy (signup link below)
./araalictl config Fog=fog.<your-customer-name-here>.aws.araalinetworks.com
./araalictl config InternalCfgBackend=prod.aws.araalinetworks.com
sudo ./araalictl authorize -local

# assessments run-locally
cd ../assessment/
```
# Links
* https://www.araalinetworks.com/signup
* https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
* https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/testing-your-ssh-connection
* https://docs.github.com/en/github/using-git/changing-a-remotes-url

# Install notebook
```
# if you have python3
pip3 install --upgrade --force-reinstall --no-cache-dir jupyter

# on kali linux
sudo apt-get install jupyter-notebook

jupyter notebook
```

# Troubleshooting
## Jupyter installation problems
You could try conda to install jupyter. Its sometimes nasty to get hold of it. We are trying to create a virtualenv for it.
## Authorization problems
```
./araalictl authorize -clean # to start over.
```
## Not able to push your branch
- https://docs.github.com/en/github/using-git/changing-a-remotes-url
- https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

