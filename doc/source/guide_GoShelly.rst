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
            git clone  git@github.com:arorasoham9/cobrashelly.git
        HTTPS::
            git clone https://github.com/arorasoham9/cobrashelly.git

    Change Directory::
        cd cobrashelly    

    Make the binary executable
        For Linux::
            chmod +x ./bin/app-amd64-linux 
        For MacOS::
            chmod +x ./bin/app-amd64-darwin

    Run the below command to make the GoShelly Server start listening
        For Linux::
            ./bin/app-amd64-linux demo
        For MacOS::
            ./bin/app-amd64-darwin demo

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
                git clone git@github.com:arorasoham9/goshelly-client.git
            HTTPS::
                git clone https://github.com/arorasoham9/goshelly-client.git

        Change Directory::
            cd goshelly-client  

        Make the binary executable::
            For Linux::
                chmod +x ./bin/app-amd64-linux 
            For MacOS::
                chmod +x ./bin/app-amd64-darwin

        Run the below command to make the GoShelly Client dial out to the backdoor server
         If you choose to use Araali's backdoor service, enter **** as the IP in the below command.
            For Linux::
                ./bin/app-amd64-linux demo --IP=<IP-address-no-port> --SSLEMAIL=<your-email>
            For MacOS::
                ./bin/app-amd64-darwin demo --IP=<IP-address-no-port> --SSLEMAIL=<your-email>
       
            

    **For K8S Cluster**
    Instructions not yet available -Soham



Installation
------------
To view results, check your Araali console.


