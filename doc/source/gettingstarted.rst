============
Installation
============

In this guide, we’ll walk you through how to install Araali software into your
Kubernetes cluster and run point-in-time assessments. We have made it easy for
you to **single-click install as well as uninstall Araali.**

**Overview:** Installing Araali is simple. The first step is to create an
account for using `Araali UI <https://console.araalinetworks.com>`_ . After
that, download the “command-line tool,” araalictl onto your your machine from
where you typically use kubectl. Authorize araalictl, start the assessment, install 
the Software you want to assess, and see the results on the Araali UI.

Requirements
*****************

You should have access to a modern Kubernetes cluster and a functioning kubectl
on your local machine. If you don’t already have a Kubernetes cluster (e.g.
EKS, GKE, AKS, RancherD), one easy option is to run one on your local machine.
There are many ways to do this, including Canonical’s production-ready
`microk8s for Ubuntu
<https://www.araalinetworks.com/post/use-araali-with-microk8s>`_

You can validate you have a working setup by running::

   kubectl version --short

You should see the output with both a Client Version and a Server Version
component.

You should have **port 443 egress open** for Araali to talk to its SaaS service

Now that you have your cluster, register your account and download araalictl

Step 1: Sign In or Register in the Araali Console
*************************************************
Visit the `Araali Console <https://console.araalinetworks.com>`_ in your browser.
If you use the Social buttons at the top of the form to sign in, there is no
registration step. If you cannot use the Social buttons, use the "Sign up" link
at the bottom of the form to sign up for an account.

.. image:: images/araali-console-sign-in.png
 :alt: Araali Console Sign In

Step 2: Download Araalictl
**************************

If this is your first time running Araali, you will need to download the
“command-line tool” araalictl onto your local machine. You can either download
it from the Araali UI or curl it in.

**To download araalictl from the Araali UI**

Navigate to Download, under Support on the left-hand panel, and download the
araalictl for your Linux or Mac machine.

.. image:: https://publicimageproduct.s3-us-west-2.amazonaws.com/araalictldownload.png
  :width: 650
  :alt: Araalictl download from Araali UI

**To curl araalictl directly to your VM,** run::

   # On Linux
   curl -O https://s3-us-west-2.amazonaws.com/araalinetworks.cf/araalictl.linux-amd64
   
   # On Mac
   curl -O https://s3-us-west-2.amazonaws.com/araalinetworks.cf/araalictl.darwin-amd64

Step 3: Authorize your Araalictl
********************************
First, make your araalictl executable::

   chmod +x araali*

   ln -sf araali* araalictl
              

Authorize your session::

   sudo ./araalictl authorize

.. image:: https://publicimageproduct.s3-us-west-2.amazonaws.com/AraalictlAuthorize.png
  :width: 650
  :alt: Araalictl authorize

Now, go to Araali UI and Navigate to Araali Tools, under Administration on the
left-hand panel.

.. image:: https://publicimageproduct.s3-us-west-2.amazonaws.com/AraaliAuthn2.png
  :width: 600
  :alt: Araali Authorization

Click on the "refresh" button if you don't see "Approve" and click to approve araalictl. Also, the session-id listed on your araalictl will match the session-id shown in the UI.

The "Approve" button should go away and you will see the "Revoke" button which
could be used to revoke the araalictl

.. image:: https://publicimageproduct.s3-us-west-2.amazonaws.com/AraaliAuthn3.png
  :width: 600
  :alt: Araali Authorization


Step 4: Validate your Araalictl installation and Kubectl
********************************************************

Go back to your VM and check if araalictl is installed properly in your system::

   ./araalictl version -v

Check if kubectl is pointing to the cluster you want to assess::

   kubectl get svc



Step 5: Run the assessment
**************************

Now, araalictl is up and running on a machine that has access to your cluster,
you can start your assessment prior to running your integration test. Araali
agents are easy to install and uninstall. You can install the software with a
single command and uninstall with a single command too::

   ./araalictl assessment -start

.. image:: https://publicimageproduct.s3-us-west-2.amazonaws.com/AraalictlAssess-start.png
  :width: 650
  :alt: Araalictl assessment -start


It might take upto a minute for the araali daemonset to start, and "Waiting for Araali firewall to start" will show SUCCESS.

Now, install all the apps that you want to test on your cluster.

After running the tests, you can stop the assessment. Community Edition allows
you to run point-in-time assessments (vs continuous monitoring/security, which
is our paid offering). So as long as your tests complete in a reasonable time,
you should have a good picture of your application. You can run the assessments
any number of times::

   ./araalictl assessment -stop


Step 6: Review the Results
****************************
You can review the results in yaml file or the Araali UI.

For yaml file 

   ./araalictl assessment -report

Or, go to the Araali UI (`console.araalinetworks.com
<https://console.araalinetworks.com>`_) and log in with the same email that was
used to authorize araalictl. 

.. image:: https://publicimageproduct.s3-us-west-2.amazonaws.com/zoneview.png
  :width: 650
  :alt: Araali Zone View

Go to the zones page in the righthand sidebar, your cluster shows as “dev”.
Click on the magnifying glass to go inside your cluster and review the
assessment results as well as a snapshot of your Kubernetes networking.



