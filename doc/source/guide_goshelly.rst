Guide for Araali GoShelly
=========================

Araali GoShelly is an open source tool that helps security teams safely test their detect and response readiness (the fire drill for SIEM/SOAR/EDR/NDR/XDR investment) 
for backdoors. This is typical when supply chain vulnerabilities like remote code execution (RCE) are exploited and represents a doomsday scenario where an attacker
has full remote control capabilities based on the backdoor.


Installation
------------

Similar to the deprecated version of this tool, Araali Shelly, GoShelly offers the option to run your own 
backdoor and/or use the already running backdoor offered by Araali to listen for incoming connections.

Setup a backdoor servivce
_________________________

To use your own backdoor server
+++++++++++++++++++++++++++++++
On a k8s cluster install and configure GoShelly server using the following instructions.
NOTE: These installation steps assume that you have Helm and kubectl - the package manager and command line tool for k8s - installed and setup already.
    1.  Add Helm repository
        ::
            helm repo add araali-helm https://araalinetworks.github.io/araali-helm/
    2.  Install GoShelly
        ::
            helm install goshelly_server araali-helm/goshelly-server
        
    1.  Install Helm chart for GoShelly Server
        ::
            helm install goshelly_server
    2.  Get the loadbalancer external IP for the client to connect to
        ::
            kubectl get svc -n goshelly-helm
        Save the external IP to the service named "goshelly-helm-port-forwarding" for later use, when setting up the GoShelly client.
    Uninstall GoShelly Server::
        helm uninstall goshelly-helm -n goshelly-helm

To use Araali's backdoor server
++++++++++++++++++++++++++++++++
Nothing. It's already running. Follow the instructions below to dial to our backdoor server using GoShelly Client.


Setup GoShelly Client
_____________________
On the machine, you wish to test the attack response readiness for, install and configure GoShelly Client 
using the following instructions.
    1.  Download Araalictl
        On Linux::

            curl -O https://s3-us-west-2.amazonaws.com/araalinetworks.cf/goshelly_linux 

        On Mac::

            curl -O https://s3-us-west-2.amazonaws.com/araalinetworks.cf/goshelly_darwin 

    2.  Make it executable
        ::
            chmod +x goshelly_*

    3.  Run the below command to make the GoShelly Client dial out to the backdoor server
        If you choose to use Araali's backdoor service use the command as shown below.
            For Linux::
                ./goshelly_linux assess
            For MacOS::
                ./goshelly_darwin assess
        If you choose to use your own backdoor service, include the loadbalancer external IP address we previously noted using IP flag as shown below.
            For Linux::
                ./goshelly_linux assess --IP <IP_ADDRESS>
            For MacOS::
                ./goshelly_darwin assess --IP <IP_ADDRESS>
    4.  Wait for GoShelly to run on your system and return results. You may also check your Araali Console to view GoShelly in action.






