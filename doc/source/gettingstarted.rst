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

Step 1: Sign In or Register in the Araali Console
*************************************************
Visit the `Araali Console <https://console.araalinetworks.com>`_ in your browser.
If you have a Gmail account, click the "Sign in with Google" button to access the Araali UI.
If you do not have a a Gmail account, use the "Sign up" button to sign up for an account.

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

   sudo ./araalictl authorize <CORRECT EMAIL ADDRESS>

   **NOTE: To correctly authorize araalictl, please enter the correct and same email used when creating an account in Araali Console.**

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


Step 4: Fortify your VM/k8s
***************************

Kubernetes
----------

Requirements
^^^^^^^^^^^^

1. You should have access to a modern Kubernetes cluster and a functioning kubectl
on your local machine. If you don’t already have a Kubernetes cluster (e.g.
EKS, GKE, AKS, RancherD), one easy option is to run one on your local machine.
There are many ways to do this, including Canonical’s production-ready
`microk8s for Ubuntu
<https://www.araalinetworks.com/post/use-araali-with-microk8s>`_

2. You can validate you have a working setup by running::

    kubectl version --short


3. You should see the output with both a Client Version and a Server Version component.

4. You should have **port 443 egress open** for Araali to talk to its SaaS service


Fortification
^^^^^^^^^^^^^
1. Check current context, the name with a "*" is the one you are pointing to right now::

    kubectl config get-contexts

2. Fortify your cluster

    * If araalictl and kubectl are running on the same machine::

        ./araalictl fortify-k8s -auto -tags=zone=<optional-zone-override> -context=<context of k8s cluster>
    * If araalictl and kubectl are not running on the same machine::

        # Create yaml file to fortify your cluster
        ./araalictl fortify-k8s -tags=zone=<optional-zone-override> -context=<context of k8s cluster>

        # The above command will generate araali_k8s.yaml file. Copy it to the k8s control plane (where kubectl is running) and then apply
        kubectl apply -f araali_k8s.yaml

3. Check if Araali is installed

    * Araali should be running in two namespaces (1) araali-operator and (2) kube-system::

        kubectl get pods -A

    .. image:: images/kubectl_post_install.png
      :width: 650
      :alt: Output of Kubectl after Araali Fortification

Uninstall Araali
^^^^^^^^^^^^^^^^^^^
If araalictl and kubectl are running on the same machine::

    ./araalictl fortify-k8s -delete -context=<context of k8s cluster>

If araalictl and kubectl are not running on the same machine::

    kubectl delete -f araali_k8s.yaml


Kubernetes - Helm Install
-------------------------

If you want to use Helm without Araalictl, contact Araali team via Slack or email us at support@araalinetworks.com

We will send you a value.yaml file like the one below for your cluster::

    araali:
      workload_id: <workloadiid>
      cluster_name: bar
      fog: foo
      zone: <poc>
      app: k8s-nodes
      enforce: true
      upgrade: true
      autok8s_image: quay.io/araalinetworks/autok8s:prod
      fw_image: quay.io/araalinetworks/araali_fw:prod
      fw_init_image: quay.io/araalinetworks/araali_fw_init:prod

You **must** change the zone name. Zone is how your cluster will show up in Araali UI.


Install Araali Repo and Run the Helm Chart
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. Install Araali Repo::

    helm repo add araali-helm https://araalinetworks.github.io/araali-helm/

2. Run the value file::

    helm install -f ./values.yaml my-araali-fw araali-helm/araali-fw

* Uninstall::

    helm uninstall my-araali-fw


VM
--

**NOTE: If you have already fortified your Kubernetes cluster, you do not need to fortify your VM as well.**

Requirements
^^^^^^^^^^^^

1. You should have a Virtual Machine already set up in order to fortify it with Araali.
    * Alternatively if you have a cluster of VMs and wish to fortify them all through a CM VM, see the :ref:`Remote Fortification` section.

2. You should have **port 443 egress open on all VMs** for Araali to talk to its SaaS service

Self Fortification
^^^^^^^^^^^^^^^^^^

1. Generate and add ssh-key (optional if you don’t have id_rsa.pub in your ~/.ssh account)::

    ssh-keygen

2. Copy it to authorized_keys to allow ssh localhost::

    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

3. Edit the sudoers file::

    sudo visudo

4. Allow for password-less sudo::

    # Scroll to the very bottom of the file, add the following line
    # Replace <user> with the user for the VM
    <user> ALL=(ALL) NOPASSWD: ALL

    # ^X to save and exit editor

5. Self-Fortify::

    ./araalictl fortify-live  -fortify -tags=zone=<zone_name>,app=<app_name> localhost

Remote Fortification
^^^^^^^^^^^^^^^^^^^^

1. Check CM VM

    * A Configuration Manager VM (CM VM) that has ssh access to the other VMs is required to remotely fortify
        .. image:: images/remote_fortification_flow.png
          :width: 650
          :alt: Setup and Networking

    It is important that araalictl is downloaded and authorized **specifically on the CM VM** so that it can remotely install Araali on the rest of the VMs


2. Remotely Fortify::

    ./araalictl fortify-live -fortify -tags=zone=<zone_name>,app=<app_name> <remote_user>@<remote_host>

To update Zone and/or App tags
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    ./araalictl fortify-live -add -tags=zone=<updated_zone>,app=<updated_app> <remote_user>@<remote_host>

**For wider use, we recommend running Araali on the same machine as your Configuration Management Tool (Ansible, Salt, Puppet, Chef, etc.)**


Uninstall Araali
^^^^^^^^^^^^^^^^^^^
Self::

    ./araalictl fortify-live -unfortify localhost


Remote::

    ./araalictl fortify-live -unfortify <remote_user>@<remote_host>


Step 5: Review the Results
****************************
You can review the results in the Araali UI or a yaml file.

Araali UI
---------

Go to the Araali UI (`console.araalinetworks.com
<https://console.araalinetworks.com>`_) and log in with the same email that was
used to authorize araalictl.

.. image:: images/top_risk_buckets.png
  :width: 650
  :alt: Araali Dashboard Insights

The Insights section on the Dashboard pull out nuggets of high priority information for you, such as

* Database, DB-as-a-Service - your crown jewels
* World Exposed Process - check for accidental exposures
* Privilege Access Process and Containers - these have over privileges and can cause significant damage if exploited
* Critical Vulnerability Containers - these are running with critical CVEs
* SaaS Services - All the SaaS services consumed by your apps
* Log4j - to identify if you have any log4j vulnerability in your environment

You can click on any of the cards to review the details.


yaml file
-----------
::

   ./araalictl assessment -report
