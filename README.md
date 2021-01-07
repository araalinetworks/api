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
app = App("zone", "app")
for link in app.iterlinks():
  if something or link.lstate != "DEFINED_POLICY":
    link.accept() # based on some side information
  if something: # based on some side information
    link.snooze()
app.review() # review what will get committed
app.commit()
```

# Relocate Policies
```
app2 = app.relocate("new_zone", "new_app")
for link in app2.iterlinks():
  # accept is the default thing on relocation for all accepted policies in ap, rest is snoozed by default
  link.snooze() # snooze the ones you dont like
  link.accept() # if you want to accept a snoozed on in original
  # relocate either client or server for the link's that need change
  link.client.relocate(...)
  link.server.relocate(...)
app2.review() # reivew what we will be committing
app2.commit()
```

# Navigation
```
run = Runtime()
run.iterstats() # dump summary stats
run.to_data() # dump all relevant data

for zone in run.iterzones(): # all the zones
    for app in zone.iterapps(): # all the apps
        for link in app.iterlinks(): # all the links
            print(link)
            break
        break
    break
    
# all apps in a zone
run.iterzones("nightly").stats()

# all links in an app
run.iterzones("nightly").iterapps("bendvm").stats()

# edit policies for an app
for link in run.iterzones("nightly").iterapps("bendvm").iterlinks():
  if something or link.lstate != "DEFINED_POLICY":
    link.accept() # based on some side information
  if something: # based on some side information
    link.snooze()
run.iterzones("nightly").iterapps("bendvm").review() # review what will get committed
run.iterzones("nightly").iterapps("bendvm").commit()
```
