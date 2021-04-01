===================================
Getting started with microk8s (Mac)
===================================

This is an end-to-end guide on how to test Araali on Canonical’s MicroK8s and use an opensource microservice app (sockshop). The most important thing is to **ensure things are running at every stage before you can proceed to the next.**


Install MicroK8s using Homebrew
************************************

Install Homebrew 
""""""""""""""""

::

   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

Once Homebrew is installed, you can proceed with Microk8s

Install MicroK8s
""""""""""""""""

::

   brew install ubuntu/microk8s/microk8s

   microk8s install

**Note: Say yes to multipass install (above)**


Check if microk8s is up::

   microk8s status --wait-ready

Before installing dns and storage, **ensure the cni is up and running by executing**::

   microk8s kubectl get pods -A


Enable the dns and ingress services::

   microk8s enable dns

   microk8s enable ingress

Before proceeding further, **ensure dns and ingress are up and running by executing**::

   microk8s kubectl get pods -A


Install Araali and start the assessment
***************************************
Follow the instructions in the `getting started post <https://araali-networks-api.readthedocs.io/en/latest/gettingstarted.html#>`_

Once Araalictl is set up, start the assessment::

 ./araalictl assessment -start


Installing an Opensource App
****************************

Download sock-shop from Github::

   git clone https://github.com/ashish234/sock-shop.git

Create a namespace::

   microk8s kubectl create ns sock-shop

Deploy the yaml file::

   microk8s kubectl apply -f sock-shop/sock-shop.yaml -n sock-shop

Look into the services and mark the port for NodePort service “front-end”::

   microk8s kubectl apply get svc -n sock-shop"

.. image:: https://publicimageproduct.s3-us-west-2.amazonaws.com/sock-shop-getsvc.png
 :width: 650
 :alt: kubectl get svc -A

In this case its running on 30001


**Open a browser and type your VM’s IP:30001**


.. image:: https://publicimageproduct.s3-us-west-2.amazonaws.com/sockshop-front-end-ui.png
 :width: 650
 :alt: sock shop frontend UI


Stop the assessment
*******************

After running the tests, you can stop the assessment::

   ./araalictl assessment -stop

Freemium only allows you to run point-in-time assessments (vs continuous monitoring/security). So as long as your tests complete in a reasonable time, you should have a good picture of your application

