Getting Started with Rafay
==========================

Prerequisites
-------------
1. Registered with Rafay and account created
2. Register with Araali to create an account to:
    * Access the UI dashboard
    * Install `araalictl` and authorize it
    * Help with generation of Helm `values.yaml`

Araali UI Login
---------------
1. Open a chrome browser and go to [Araali Console](https://console.araalinetworks.com)
    ![Araali Sign-In](images/updated-araali-console-signin.png "Araali UI Sign-In")
&nbsp;   

2. Click `Sign Up` to register
3. You are in!!
4. Now, in the left-hand panel, go to Administration and then Araali Tools. You will use this page to authorize Araalictl
    ![Araali Authorization Dashboard](images/araali-auth-dash.png "Araali Authorization Dashboard")
   

Generating Helm `values.yaml`
-----------------------------
__Follow the steps below to generate a `values.yaml` file to use with Araali Helm chart for your cluster.__


### Setup

1. Download Araalictl 
   * On Linux
      ```console
      curl -O https://s3-us-west-2.amazonaws.com/araalinetworks.cf/araalictl.linux-amd64
      ```
   * On Mac
      ```console
      curl -O https://s3-us-west-2.amazonaws.com/araalinetworks.cf/araalictl.darwin-amd64
      ```
&nbsp;   

2. Make it executable
   ```console
   chmod +x araali*
   ln -sf araali* araalictl
   ```
3. Authorize araalictl
   ```console
   sudo ./araalictl authorize <email-id>
   ```
&nbsp;

4. Now go to Araali UI >> Administration >> Araali Tools to approve the araalictl session.
   ![Araalictl Approval](images/araalictl-approve.png "Araalictl Approval")


### Execution

1. Check if araalictl is installed
    ```console
    ./araalictl version -v
    ```
&nbsp;

2. Generate helm values::
    ```console
    ./araalictl fortify-k8s -out=helm > /tmp/values.yaml
    ```

Create Rafay Repository for Araali Helm chart access
----------------------------------------------------

Add Araali Helm repository to Rafay
- [Create Rafay Araali Helm Registry](https://console.rafay.dev/#/app/repositories)
  ![Create Araali Helm Repo in Rafay](images/rafay-araali-helm-registry.png "Create Araali Helm Repo in Rafay")


*The Rafay repository will be used in the Araali addon below*

Create Rafay AddOn for Araali Firewall
--------------------------------------

Add Araali addon to Rafay 
- [Create Rafay Araali AddOn](https://console.rafay.dev/#/app/addons)

1. Click on `New AddOn`
   ![Create Araali AddOn in Rafay](images/rafay-araali-new-addon.png "Create Araali AddOn in Rafay")
&nbsp;

2. Click on `New Version`
   ![Create Araali AddOn Version in Rafay](images/rafay-araali-new-addon-version.png "Create Araali AddOn Version in Rafay")
&nbsp;   

3.
    Upload the previously created `values.yaml` file
    ```console
    Chart Name: araali-fw Chart Version: 1.0.0
    ```
&nbsp;
4. Edit the `values.yaml` in Rafay to get the runtime clustername from Rafay.
   ![Edit values.yaml in Rafay](images/rafay-araali-new-addon-edit.png "Edit values.yaml in Rafay")
   
*The Rafay addon will be used in the Araali Blueprint below*

Create Rafay Blueprint that uses Rafay AddOn
--------------------------------------------

Add Araali blueprint to Rafay 
- [Create Rafay Araali Blueprint](https://console.rafay.dev/#/app/blueprints)

1. Click on `New AddOn`
   ![Create Araali Blueprint in Rafay](images/rafay-araali-new-blueprint.png "Create Araali Blueprint in Rafay")
&nbsp;

2. Click on `New Version`
   ![Create Araali Blueprint Version in Rafay](images/rafay-araali-new-blueprint-version.png "Create Araali Blueprint Version in Rafay")
&nbsp;

3. Use the addon created above in the add `AddOn` section

*This blueprint will be applied to the cluster*

Enable Rafay Blueprint on the cluster
-------------------------------------
Add Araali Blueprint to Rafay
- [Create Rafay Araali Blueprint](https://console.rafay.dev/#/app/blueprints>)

1. Click on the settings wheel icon and select ``Update Blueprint``
   ![Add Araali Blueprint to cluster](images/rafay-araali-cluster-add-blueprint.png "Add Araali Blueprint to cluster")
&nbsp;

2. Pick the Blueprint and Version created in previous step
   ![Add Araali Blueprint Version to Cluster in Rafay](images/rafay-araali-cluster-save-blueprint.png "Add Araali Blueprint Version to Cluster in Rafay")
&nbsp;
   
*Once the changes are saved, the Araali add on is __activated in the cluster__.
Check for the sync to finish and visit the Araali Dashboard for instant visibility into your cluster.*

Araali Dashboard
----------------

Go back to the Araali UI and click dashboard. You can see an inventory of your assets covered as well as detailed audits of your communication.

![Araali Dashboard](images/araali-dash.png "Araali Dashboard")

Uninstalling Araali
-------------------

Select the default blueprint and apply it to the cluster