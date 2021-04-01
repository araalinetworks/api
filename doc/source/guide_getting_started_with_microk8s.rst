=============================
Getting Started with microk8s
=============================

This is an end-to-end guide on how to test Araali on Canonical’s MicroK8s and use an opensource microservice app (sockshop).

Install MicroK8s
*******************

Start with an Ubuntu 18 VM to install microk8s

   ``sudo snap install microk8s --classic --channel=1.19``


Join the Group

   ``sudo usermod -a -G microk8s $USER``
   ``sudo chown -f -R $USER ~/.kube``

Exit and log back to the VM

Check if microk8s is up

   ``microk8s status --wait-ready``

Create a link/alias
   ``sudo snap alias microk8s.kubectl mkctl``

Now use mkctl like kubectl. 
If you DONT want the alias then use “microk8s.kubectl” command similar to “kubectl"

Enable the dns and ingress services

   ``microk8s enable dns``

   ``microk8s enable ingress``

Install Araali and start the assessment
***************************************
Follow the instructions in the `getting started post <https://araali-networks-api.readthedocs.io/en/latest/gettingstarted.html#>`_

Once Araalictl is set up, start the assessment

 ``./araalictl assessment -start``

If you don't want microk8s to be preferred even when you have it installed. Run with the `-ignoreMK8S` option set to true::

 ./araalictl assessment -start -ignoreMK8S=true

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


Stop the assessment
***********************

After running the tests, you can stop the assessment. 
   ``./araalictl assessment -stop``

Freemium only allows you to run point-in-time assessments (vs continuous monitoring/security). So as long as your tests complete in a reasonable time, you should have a good picture of your application
