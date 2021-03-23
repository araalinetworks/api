.. Araali Networks API documentation master file, created by
   sphinx-quickstart on Mon Mar 22 13:38:13 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Araali Networks API's documentation!
===============================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Getting Started
=================

In this guide, we’ll walk you through how to install Araali into your Kubernetes cluster and run point-in-time assessments. We have made it easy for you to **Single-click install and uninstall Araali.**

**Overview:** Installing Araali is simple. First, get registered with Araali by sending a simple email to support@araalinetworks.com that you want to try out. You will receive an email from us once your account is provisioned. After that, download the “command-line tool”, araalictl onto your Kubernetes control plane VM. Authorize araalictl, run the assessment, and see the results on Araali UI.

Step 0: Setup
*****************

Before we can do anything, we need to ensure you have access to the modern Kubernetes cluster and a functioning kubectl on your local machine. (If you don’t already have a Kubernetes cluster, one easy option is to run one on your local machine. There are many ways to do this, e.g. EKS, GKE, AKS, RancherD, Canonical’s production-ready `microk8s for Ubuntu <https://www.araalinetworks.com/post/use-araali-with-microk8s>`_
, and more.)

You can validate your setup by running:

   ``kubectl version --short``

You should see the output with both a Client Version and Server Version component.

Now that we have our cluster, we’ll download araalictl

Step 1: Download Araalictl
**************************
If this is your first time running Araali, you will need to download the “command-line tool” araalictl onto your local machine. You can download it from the Araali UI or curl it.

**To download araalictl from the Araali UI**, go to console.araalinetworks.com and log in. Navigate to Download, under Support on the left-hand panel, and download the araalictl for your Linux or Mac machine.

.. image:: https://publicimageproduct.s3-us-west-2.amazonaws.com/araalictldownload.png
  :width: 650
  :alt: Alternative text

To curl araalictl directly to your VM, run:

Linux

   ``curl -O https://s3-us-west-2.amazonaws.com/araalinetworks.cf/araalictl.linux-amd64``

Mac

   ``curl -O https://s3-us-west-2.amazonaws.com/araalinetworks.cf/araalictl.darwin-amd64``

Step 2: Authorize your Araalictl
********************************

First, make your araalictl executable.

   ``chmod +x araali*``

   ``ln -sf araali* araalictl``

If this is your **first time** using Araali, we will provision your freemium account in our backend once you send an email to support@araalinetworks.com (step above)

Once you are provisioned you will get a Welcome Email from Araali. Come back to your VM and run authorize, to authorize your session.

   ``sudo ./araalictl authorize``

Now, go to your email and look for an approval email from Araali. Click on “Approve” to authenticate your araalictl session.

.. image:: https://publicimageproduct.s3-us-west-2.amazonaws.com/araaliauthenticationemail.png
  :width: 600
  :alt: Alternative text

Authentication email sent to your account.



Step 3: Validate your Araalictl installation and Kubectl
********************************************************

Check if araalictl is installed properly in your system.

   ``./araalictl version -v``

Check if kubectl is pointing to the cluster you want to assess.

   ``kubectl get svc``



Step 4: Run the assessment
**************************

Now, araalictl is up and running on a machine that has access to your cluster, you can start your assessment prior to running your integration test. Araali agents are easy to install and uninstall. You can install the software with a single command and uninstall with a single command too.

   ``./araalictl assessment -start``

Make sure you have all apps that you want to test, installed on your cluster. If not, go ahead and install them.

After running the tests, you can stop the assessment. Freemium only allows you to run point-in-time assessments (vs continuous monitoring/security). So as long as your tests complete in a reasonable time, you should have a good picture of your application

   ``./araalictl assessment -stop``


Step 5: Review the Results
**************************

Go to the Araali UI (`console.araalinetworks.com <https://console.araalinetworks.com>`_
) and log in with the same email that was used to authorize araalictl.

.. image:: https://publicimageproduct.s3-us-west-2.amazonaws.com/zoneview.png
  :width: 650
  :alt: Alternative text

Go to the zones page in the righthand sidebar, your cluster shows as “dev”. Click on the magnifying glass to go inside your cluster and review the assessment results as well as a snapshot of your Kubernetes networking.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
