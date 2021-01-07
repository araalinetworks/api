# Getting Started
```
mkdir araalinetworks
git clone https://github.com/araalinetworks/api.git
cd api/python

# install/upgrade
python araalictl.py

# to authorize your copy (signup link below)
./araalictl authorize
```
# Links
* https://www.araalinetworks.com/signup
* https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
* https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/testing-your-ssh-connection

# Accept policies
```
ap = AppPolicy(zone, app)
for link in ap.iterlinks():
  if something or link.lstate != "DEFINED_POLICY":
    link.accept() # based on some side information
  if something: # based on some side information
    link.snooze()
ap.review() # review what will get committed
ap.commit()
```

# Relocate Policies
```
ap2 = ap.relocate(new_zone, new_app)
for link in ap2.iterlinks():
  # accept is the default thing on relocation for all accepted policies in ap, rest is snoozed by default
  link.snooze() # snooze the ones you dont like
  link.accept() # if you want to accept a snoozed on in original
  # relocate either client or server for the link's that need change
  link.client.relocate(...)
  link.server.relocate(...)
ap2.review() # reivew what we will be committing
ap2.commit()
```
