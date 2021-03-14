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
```
# Links
* https://www.araalinetworks.com/signup
* https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
* https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/testing-your-ssh-connection
* https://docs.github.com/en/github/using-git/changing-a-remotes-url
```

# Troubleshooting
## Authorization problems
```
./araalictl authorize -clean # to start over.
```
## Not able to push your branch
- https://docs.github.com/en/github/using-git/changing-a-remotes-url
- https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

