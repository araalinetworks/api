# Getting Started
```
mkdir araalinetworks
cd araalinetworks
git clone https://github.com/araalinetworks/api.git
cd api/python

# install/upgrade
python araalictl.py

# to authorize your copy (signup link below)
./araalictl authorize -local
./araalictl config InternalCfgBackend=prod.aws.araalinetworks.com
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
  # edit/generalize using regex: client or server for the link's that need change
  link.client.change("binary_name", "/snap/amazon-ssm-agent/[0-9]+/ssm-agent-worker")
  link.server.change("binary_name", "/snap/amazon-ssm-agent/[0-9]+/ssm-agent-worker")
app2.review() # reivew what we will be committing
app2.commit()
```

# Navigation and Drilldown - organized by hierarchies
```
run = Runtime()
run.stats() # dump summary stats
run.to_data() # dump all relevant data

for zone in run.iterzones(): # all the zones
    for app in zone.iterapps(): # all the apps
        for link in app.iterlinks(): # all the links
            print(link)
            break
        break
    break
    
# stats for all apps in a zone
run.iterzones("zone").stats()

# stats for all links in an app
run.iterzones("zone").iterapps("app").stats()

# edit policies for an app
for link in run.iterzones("zone").iterapps("app").iterlinks():
  if something or link.lstate != "DEFINED_POLICY":
    link.accept() # based on some side information
  if something: # based on some side information
    link.snooze()
run.iterzones("zone").iterapps("app").review() # review what will get committed
run.iterzones("zone").iterapps("app").commit()

# accept all open alerts for zone/app
for link in run.iterzones("zone").iterapps("app").iterlinks(afilter=True):
    print(link)
    link.accept()
    
# review changes before commit
run.iterzones("zone").iterapps("app").review()
run.iterzones("zone").iterapps("app").commit()
```

# Table with filters - all the world's a flat filtered table
```
run = Runtime()

stats = Table(run.stats(all=False))
total_alerts = sum([a["Num Links"] for a in stats.to_data()])

# library of commonly used filters
f = LinkTable.Filter

# all the links in your runtime, arbitrarly chain lambdas as filters)
linkTable = LinkTable(run.iterlinks(),
          #f.endpoint("zone", "prod"),
          #f.endpoint("app", "^bendvm.bend.web"),
          #f.endpoint("dns_pattern", "169"),
          #f.endpoint("dns_pattern", "api.snapcraft.io"),
          #f.neg(f.endpoint("dns_pattern", None, who="server")),
          #f.endpoint("network", None, who="server"),
          #f.endpoint("network", None, who="client"),
          #f.endpoint("network", "169.254.169.254", who="server")
          #f.neg(f.endpoint("process", ansible", re.IGNORECASE)),
          #f.endpoint("binary_name", "/snap/amazon-ssm-agent"), #/2996/ssm-agent-worker")
          #f.neg(f.endpoint("process", "cassandra", re.IGNORECASE)),
          #f.endpoint("process", ["sshd", "haproxy"], who="server"),
          #f.endpoint("network", None, who="server"), # perimeter
          #f.neg(f.endpoint("dns_pattern", None, who="server")),
          #f.neg(f.endpoint("network", None, who="server")), # perimeter          
          #f.ltype("NAE"),
          f.lstate("BASELINE_ALERT"),
          #f.speculative(False),
          #f.lstate("DEFINED_POLICY"),
          #f.neg(f.server_non_ip),
          #f.server_non_ip,
          #f.perimeter,
          #f.neg(f.same_zone),
          #f.same_zone
         )
         
linkTable.snooze() # EITHER, snooze all links that pass the filter
linkTable.accept() # OR, accept all links that pass the filter

# multi-link editing: assuming all links are homogeneous
linkTable.change("client", "binary_name", "/snap/amazon-ssm-agent/[0-9]+/ssm-agent-worker")

# done with all filtering and editing
run.review()
run.commit()
```
