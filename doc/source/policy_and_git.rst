Policy and Git
==============

Provisioning Policies from Git
------------------------------

On every deployment of an app that needs to be secured, we can clean and apply
policies that were saved in the git repo as part of ops for that app. This
ensures that we always start from a clean state where we only allow the
links that we have already reviewed and approved.

1. Generate and apply the Araali firewall installation yaml with the AraaliPolicy
CRD enabled.

2. Modify the Service Discovery config to start watching Araali policy lifecycle.
    .. code-block:: python

       araalictl fortify-k8s -tags=zone=policy-1 -araali-policy-crd -force policy-1

       kubectl edit cm araali-operator-config -n araali-operator
       araalitags.operator.araali_k8s_policy_enable: "1" (Add this to configmap)

       kubectl apply -f araali_k8s.yaml

3. Apply the Araali policy from git before deploying application.

    .. code-block:: python

       kubectl apply -f /tmp/yaml/common.voting-tmp.yaml -n voting-tmp (K8S)
       cat /tmp/yaml/common.voting-tmp.yaml | araalictl policy -zone=policy-1 -app=voting-tmp -tenant=vmk -op update (VM)

4. Check UI for policy

    .. image:: images/aks-voting-app-new.png
     :width: 800
     :alt: AKS Voting App

With this workflow, Araali automates the task of writing network security
policy and managing its lifecycle using git ops. After these policies are
discovered, the app can use them on any cluster or even other clouds!

Pushing Policies to Git
-----------------------
Once we are satisfied with the review of the links for an app, we can fetch the
links in yaml format using our command-line tool araalictl by following the steps below.

1. Download the reviewed and accepted policy for an application (rsncommon/voting)

    .. code-block:: python

       araalictl policy -zone=rsncommon -app=voting -tenant=rsn > /tmp/yaml/common.voting.yaml

2. Use the AKS voting app running in ``rsncommon`` zone and ``voting`` namespace.

    .. image:: images/aks-voting-app.png
     :width: 800
     :alt: AKS Voting App

3. Modify the zone, app and any other fields that need to be edited and save them into a different
file. *In this example the zone and app will be modified to (policy-1/voting-tmp)*

4. Check your policy diff visually to make sure it is ok

    .. code-block:: python

       araalictl policy -file1 /tmp/yaml/common.voting.yaml -file2 /tmp/yaml/common.voting-tmp.yaml -op=diff

5. Note down the URL presented by the policy diff API. This is a persistant URL that can be
passed around for policy review.

    .. code-block:: python

       araalictl policy -diff-id=74c05743-a25c-45e4-8dd8-1f27956b690c

6. Commit the new policy file (/tmp/yaml/common.voting-tmp.yaml) to git along side the application.

We can repeat the discovery and review process to come up with good allowed
policies. We should also be able to view the difference between policies in the
file on the our git repo and the current status of links in the app, all on our
UI.

Saving policies in git also help with versioning the policies which allow us to
iterate over the discovery and review process.

