============================
Getting Started with AWS EKS
============================

Install AWS EKS with eksctl
***************************

Skip this part and go to "Test if you have access" if you have already installed or have access to an AWS EKS cluster and a functioning kubectl on your local machine.

Install eksctl by following instructions in this `doc <https://docs.aws.amazon.com/eks/latest/userguide/getting-started-eksctl.html>`_

This is a good way to choose Ubuntu AMI for the node machine. The console approach does not allow you to launch Ubuntu AMI.

Create a cluster and Nodes
--------------------------

This will create a cluster using Ubuntu AMI. If you don't choose an AMI it will pick AmazonLinux::

   eksctl create cluster --node-ami=Ubuntu1804

This will attach node groups to the cluster::

   eksctl create nodegroup --cluster=floral-sculpture-1600963464 \
        --name=testu --node-ami-family Ubuntu1804  --node-volume-size=45 \
        --ssh-public-key="~/.ssh/key1.pub"

Access your cluster
-------------------

After the k8s cluster and nodes are created (either through CLI or console), the next step is to access it::
 
   aws eks --region us-west-2 update-kubeconfig --name k8s-test-cluster

This will add cluster information to kubectl config file generally sitting in /home/ec2-user/.kube/config

Test if you have access to the cluster
--------------------------------------
::
  
  kubectl get svc -A

Check which cluster you  are connected to::
  
   kubectl config current-context

Install Araali
***************************************
Follow the instructions in the `getting started post <https://araali-networks-api.readthedocs.io/en/latest/gettingstarted.html#>`_


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
