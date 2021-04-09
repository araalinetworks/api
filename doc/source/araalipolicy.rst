===========================
Araali Policies with GitOps
===========================

Discover Policies
-----------------

One of the most beneficial features of Araali is its policy paradigm. It automatically discovers policies for every namespace/app - no need to write declarative policies. Besides, Araali uses identity instead of IP and Port for policies. The identity paradigm is more relevant in the modern cloud-native environment where IPs are ephemeral. Araali’s identity is inspired by `SPIFFE/SPIRE <https://github.com/spiffe/spire>`_. 


.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/araalipolicy0.png
 :width: 800
 :alt: Araali k8s Support Matrix


When you run Araali assessment, it discovers the communication between services identities and automatically suggests those policies as a diagram. In the diagram, each box represents a process. It will have an identity if Araali is running or a DNS or IP address if there is no Araali. The lines between these boxes represent network communication - all the links will start their lifecycle as alerts as shown in the above diagram.

Review Policies
---------------

Araali provides various ways of reviewing the links once we are done with the discovery step. We can verify the communication pattern of an application through our UI or our API. Links that were discovered can be transitioned to one of the following states.

1. Allowed
""""""""""

Links accepted as whitelist policy.

2. Snoozed
""""""""""
A snoozed link is forgotten. It will show up again if a new flow is observed. Typically links are snoozed when the underlying problem is addressed. It is snoozed so that there is a notification on subsequent occurrences.
We will be able to snooze erroneous whitelisted/denied policies as well.

3. Denied
"""""""""
A denied link is snoozed forever. You neither want to accept nor snooze because you are aware of it and don’t want to be bothered by it again.

Review using Araali UI
----------------------
We drill down to the app page from the zone page selecting the zone we are interested in and from there we choose the app we are interested in and land on our policy page for that app. 


.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/araalipolicy1.png
 :width: 800
 :alt: Araali k8s Support Matrix


1. Accepting
""""""""""""
a. Choose the red line for each connection that you want to approve.
b. Choose the check mark. The line turns green.

Validate and accept all approved connections. This converts them to policies.

That’s it—you have created allow-list policies for your app! No need to **manually discover and write declarative** policies.

2. Snoozing
"""""""""""

a. Choose the red line for each connection that you want to snooze.
b. Choose the timer icon. The line turns blue and is hidden by default.

3. Denying
""""""""""

a. Choose the red line connection you’d like to snooze forever.
b. Choose the bell icon. The line turns yellow.

The snapshot below shows some of the transitions made on our UI.

.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/araalipolicyactiontaken.png
 :width: 800
 :alt: Araali k8s Support Matrix




Review using Araali API
-----------------------

The above data can be accessed as python objects as well using our API. We can set up python API as described `here <https://github.com/araalinetworks/api>`_.

1. Fetching links for a given zone and app.
"""""""""""""""""""""""""""""""""""""""""""

.. code-block:: python

   import API
   app = api.App("azuref", "wordpress")

   # We can access the links part of the app as below.
   for link in app.iterlinks():
     link.to_data()

2. Once we have the links we can take the following actions.
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

a. Accept an alert as defined policy.

.. code-block:: python

   app.links[0].accept()


b. Deny an alert / defined policy.

.. code-block:: python
   
   app.links[0].deny()


c. Snooze an alert / defined policy / denied policy.

.. code-block:: python
   
   app.links[0].snooze()


Pushing policies to git
-----------------------
Once we are satisfied with the review of the links for an app. We can fetch the links in yaml format using our command-line tool araalictl as shown in the example below.

.. code-block:: python

 - client:
      zone: azuref
      app: wordpress.wpapp-wordpress.wordpress
      process: httpd
      binary_name: /opt/bitnami/apache/bin/httpd
      parent_process: httpd
    server:
      dns_pattern: ':api.wordpress.org:'
      dst_port: 443
      endpoint_group: wordpress.org
    type: NAE
    speculative: false
    state: DEFINED_POLICY
    timestamp: 1617828767000
    unique_id: id://azuref,:wordpress.wpapp- 
 wordpress.wordpress:,httpd,httpd,/opt/bitnami/apache/bin/httpd+++api.wordpress.org:443+++false+++false
   rollup_ids:
   - id://azuref,:wordpress.wpapp- 
 wordpress.wordpress:,httpd,httpd,/opt/bitnami/apache/bin/httpd+++api.wordpress.org:443+++false+++false
  active_ports:
   - 443

The above-saved file can be committed to a git repository::

   $ git checkout -b azuref
   $ git add azuref.policies.v1.yaml
   $ git commit -m "Adding azuref accepted policies."
   $ git push -u origin azuref

We can repeat the discovery and review process to come up with good allowed policies. We should also be able to view the difference in the policies in the file checked into a git repo with the current status of links in the app on our UI.

Saving policies in git also help with versioning the policies which allow us to iterate over the discovery and review process.


Provisioning policies from git
------------------------------

On every deployment of an app that needs to be secured, we can clean and apply policies that were saved in the git repo as part of ops for that app. This ensures that we always start from a pristine state where we only allow the links that we have already reviewed and approved. 

We can follow these steps as part of the app deployment process.

a. Clear policies - Our command-line tool araalictl offers the options of cleaning the policies for a given app in a specific zone::

    $ ./araalictl api -clear-policies -zone=azuref -app=wordpress

b. Apply policies from git - Use the push-policies command supported by araalictl and pipe the contents of the policy file from git::

   $ cat azuref.policies.v1.yaml | ./araalictl api -push-policies -zone=azuref -app=wordpress

c. Finally, deploy your app.

With this workflow, Araali automates the task of writing network security policy and managing its lifecycle using git ops. After these policies are discovered, the app can use them on any cluster or even other clouds!
