============================
Getting Started with GKE/AKS
============================

Requirements
*****************

You should have access to a cluster on GKE and a functioning kubectl on your local machine.

You can validate your kubectl by running::

   kubectl version --short

Check if kubectl is pointing to the cluster you want to assess::

   kubectl get svc

Install Araali and start the assessment
***************************************
Follow the instructions in the `getting started post <https://araali-networks-api.readthedocs.io/en/latest/gettingstarted.html#>`_

Once Araalictl is set up, start the assessment::

 ./araalictl assessment -start

Setting up an app to test
*************************

Download the google-microservice-shopping app from GitHub::

   git clone https://github.com/GoogleCloudPlatform/microservices-demo.git

Go to the directory::

   cd microservices-demo/release

Create a namespace::

   kubectl create ns gshop

Run the file::

   kubectl apply -f kubernetes-manifests.yaml --namespace=gshop

Get the IP for external service to log from a browser::

   kubectl get svc -A

FrontEnd

.. image:: https://publicimageproduct.s3-us-west-2.amazonaws.com/googleappfrontend.png
  :width: 600
  :alt: Google Shopping App Front End


Stop the assessment
***********************

After running the tests, you can stop the assessment::

   ./araalictl assessment -stop

Freemium only allows you to run point-in-time assessments (vs continuous monitoring/security). So as long as your tests complete in a reasonable time, you should have a good picture of your application

