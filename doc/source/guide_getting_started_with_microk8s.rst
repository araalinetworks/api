======================================
Getting Started with microk8s (Ubuntu)
======================================

This is an end-to-end guide on how to test Araali on Canonical’s MicroK8s and use an opensource microservice app (sockshop).

Install MicroK8s
*******************

Start with a VM running Ubuntu. For demonstration purposes, Ubuntu 21.10 is used here. 
Install MicroK8s with the following command to get periodic snap updates of Microk8s to ensure compatibily with newer Ubuntu releases:

   ``sudo snap install microk8s --classic --channel=latest/stable``


Join the Group

   ``sudo usermod -a -G microk8s $USER``
   ``sudo chown -f -R $USER ~/.kube``

Exit and log back to the VM

Check if microk8s is up

   ``microk8s status --wait-ready``
If the above command does not return any output, it is likely that an error occured.
Remove the same command without the ``--wait-ready`` flag to know any errors and/or warnings.

Create a link/alias
   ``sudo snap alias microk8s.kubectl mk``

Now use mkctl like kubectl. 
If you DONT want the alias then use “microk8s.kubectl” command similar to “kubectl"

Enable the dns and ingress services

   ``microk8s enable dns``

   ``microk8s enable ingress``

Install Araali and start the assessment
***************************************
Follow the instructions in the `getting started post <https://araali-networks-api.readthedocs.io/en/latest/gettingstarted.html#>`_

Install an Opensource App
****************************

Download sock-shop from Github

   ``git clone https://github.com/ashish234/sock-shop.git``

Create a namespace
   ``mkctl create ns sock-shop``

Deploy the yaml file

   ``mkctl apply -f sock-shop/sock-shop.yaml -n sock-shop``

Look into the services and mark the port for NodePort service “front-end”

.. image:: https://publicimageproduct.s3-us-west-2.amazonaws.com/sock-shop-getsvc.png
 :width: 650
 :alt: kubectl get svc -A

In this case its running on 30001


**Open a browser and type your VM’s IP:30001**


.. image:: https://publicimageproduct.s3-us-west-2.amazonaws.com/sockshop-front-end-ui.png
 :width: 650
 :alt: sock shop frontend UI


