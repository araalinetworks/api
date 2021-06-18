=============================
Understanding Araali Policies
=============================

Araali Policies
===============

Discover
--------

One of the most beneficial features of Araali is its policy paradigm. It
automatically discovers policies for every namespace/app - no need to write
declarative policies. Besides, Araali uses identity instead of IP and Port for
policies. The identity paradigm is more relevant in the modern cloud-native
environment where IPs are ephemeral. Araali’s identity is inspired by
`SPIFFE/SPIRE <https://github.com/spiffe/spire>`_. 

.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/araalipolicy0.png
 :width: 800
 :alt: Araali k8s Support Matrix

When you run Araali assessment, it discovers the communication between services
identities and automatically suggests those policies as a diagram. In the
diagram, each box represents a process. It will have an identity if Araali is
running or a DNS or IP address if there is no Araali. The lines between these
boxes represent network communication - all the links will start their
lifecycle as alerts as shown in the above diagram.

Review
------

Araali provides various ways of reviewing the links once we are done with the
discovery step. We can verify the communication pattern of an application
through our UI or our API. Links that were discovered can be transitioned to
one of the following states.

1. Allowed
""""""""""

Links accepted as whitelist policy.

2. Snoozed
""""""""""
A snoozed link is forgotten. It will show up again if a new flow is observed.
Typically links are snoozed when the underlying problem is addressed. It is
snoozed so that there is a notification on subsequent occurrences.

We will be able to snooze erroneous whitelisted/denied policies as well.

3. Denied
"""""""""
A denied link is snoozed forever. You neither want to accept nor snooze because
you are aware of it and don’t want to be bothered by it again.

Enforce
-------
Once policies are reviewed, they are ready to be enforced. Creating guard rails
and monitoring for deviations vs enforcing them upfront is a business decision
that depends on the value of the resource being protected. Araali allows you to
make these decisions at a very fine granularity - at a per app and per service
level

Managing policies in Araali UI
==============================
We drill down to the app page from the zone page selecting the zone we are
interested in and from there we choose the app we are interested in and land on
our policy page for that app. 


.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/araalipolicy1.png
 :width: 800
 :alt: Araali k8s Support Matrix


1. Accepting
------------
a. Choose the red line for each connection that you want to approve.
b. Choose the check mark. The line turns green.

Validate and accept all approved connections. This converts them to policies.

That’s it—you have created allow-list policies for your app! No need to
**manually discover and write declarative** policies.

2. Snoozing
-----------

a. Choose the red line for each connection that you want to snooze.
b. Choose the timer icon. The line turns blue and is hidden by default.

3. Denying
----------

a. Choose the red line connection you’d like to snooze forever.
b. Choose the bell icon. The line turns yellow.

The snapshot below shows some of the transitions made on our UI.

.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/araalipolicyactiontaken.png
 :width: 800
 :alt: Araali k8s Support Matrix



GitOps with Araali API
======================

The above data can be accessed as python objects as well using our API. We can
set up python API as described `here <https://github.com/araalinetworks/api>`_.

1. Fetching links for a given zone and app.
-------------------------------------------

.. code-block:: python

   import API
   app = api.App("azuref", "wordpress")

   # We can access the links part of the app as below.
   for link in app.iterlinks():
     link.to_data()

2. Once we have the links we can take the following actions.
------------------------------------------------------------

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
Once we are satisfied with the review of the links for an app. We can fetch the
links in yaml format using our command-line tool araalictl as shown in the
example below.

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

We can repeat the discovery and review process to come up with good allowed
policies. We should also be able to view the difference in the policies in the
file checked into a git repo with the current status of links in the app on our
UI.

Saving policies in git also help with versioning the policies which allow us to
iterate over the discovery and review process.


Provisioning policies from git
------------------------------

On every deployment of an app that needs to be secured, we can clean and apply
policies that were saved in the git repo as part of ops for that app. This
ensures that we always start from a pristine state where we only allow the
links that we have already reviewed and approved. 

We can follow these steps as part of the app deployment process.

a. Clear policies - Our command-line tool araalictl offers the options of
cleaning the policies for a given app in a specific zone::

    $ ./araalictl api -clear-policies -zone=azuref -app=wordpress

b. Apply policies from git - Use the push-policies command supported by
araalictl and pipe the contents of the policy file from git::

   $ cat azuref.policies.v1.yaml | ./araalictl api -push-policies -zone=azuref -app=wordpress

c. Finally, deploy your app.

With this workflow, Araali automates the task of writing network security
policy and managing its lifecycle using git ops. After these policies are
discovered, the app can use them on any cluster or even other clouds!

App Re-Mapping
==============

Araali hierachically organizes applications deployed in Kubernetes by “Zone”
and “App”, where "Zone" maps to a Kubernetes cluster and "App" maps to the
Kubernetes namespace inside which the application was deployed. Usually, each
application is deployed in its own namespace. However, in some organizations
namespace could be for an entire team's use or for an entire environment (prod,
dev, staging). In such cases, the namespace gets pretty big and Araali allows
the flexibility of mapping pods into applications the way it is generally
understood by developers.

This is accomplished by remapping the set of pods discovered in Kubernetes.
Remapping is a flexible and powerful construct that allows users to group a
specific set of Kubernetes pods under an app even though they run as part of a
single namespace.

Below is a sample google shopping application where all the pods show up under
a single app - gshop. We’ll walk through the process of splitting this up into
three different apps.

.. image:: https://raw.githubusercontent.com/araalinetworks/attacks/main/images/manypodsonenamespace.png
 :width: 600
 :alt: Many apps in a single namespace

a. List all current apps to pod mapping as yaml::

    $ ./araalictl api -list-pod-mappings > pod_mapping.yaml

b. Update the mapping yaml file.

   1. By default, the app name is same as the namespace.
   2. The user can change the name of the app (app tag) as desired.

   This can be done programmatically as well. Here we show a manual way of editing the yaml files.

   Below is a sample yaml file generated::

     cat pod_mapping.yaml

   .. code-block::

    - zone: prod
      namespace: gshop
      pod: checkoutservice
      app: gshop
    - zone: prod
      namespace: gshop
      pod: frontend
      app: gshop
    - zone: prod
      namespace: gshop
      pod: cartservice
      app: gshop
    - zone: prod
      namespace: gshop
      pod: recommendationservice
      app: gshop
    - zone: prod
      namespace: gshop
      pod: currencyservice
      app: gshop
    - zone: prod
      namespace: gshop
      pod: shippingservice
      app: gshop
    - zone: prod
      namespace: gshop
      pod: adservice
      app: gshop
    - zone: prod
      namespace: gshop
      pod: redis-cart
      app: gshop
    - zone: prod
      namespace: gshop
      pod: productcatalogservice
      app: gshop
    - zone: prod
      namespace: gshop
      pod: emailservice
      app: gshop
    - zone: prod
      namespace: gshop
      pod: paymentservice
      app: gshop

   Now we would like to re-map the pods as below.

     1. frontend → gshop-frontend
     2. redis-cart → gshop-db
     3. rest of the services → gshop-service

   .. code-block::

    - zone: prod
      namespace: gshop
      pod: checkoutservice
      app: gshop-service
    - zone: prod
      namespace: gshop
      pod: frontend
      app: gshop-frontend
    - zone: prod
      namespace: gshop
      pod: cartservice
      app: gshop-service
    - zone: prod
      namespace: gshop
      pod: recommendationservice
      app: gshop-service
    - zone: prod
      namespace: gshop
      pod: currencyservice
      app: gshop-service
    - zone: prod
      namespace: gshop
      pod: shippingservice
      app: gshop-service
    - zone: prod
      namespace: gshop
      pod: adservice
      app: gshop-service
    - zone: prod
      namespace: gshop
      pod: redis-cart
      app: gshop-db
    - zone: prod
      namespace: gshop
      pod: productcatalogservice
      app: gshop-service
    - zone: prod
      namespace: gshop
      pod: emailservice
      app: gshop-service
    - zone: prod
      namespace: gshop
      pod: paymentservice
      app: gshop-service

c. Update the pod to app mapping in araali::

       cat pod_mapping.yaml | ./araalictl api -update-pod-mappings

   Once the above exercise is complete, we see that in Araali UI the namespace
   was split and remapped into three different apps as shown below.

   .. image:: https://raw.githubusercontent.com/araalinetworks/attacks/main/images/manypodsthreeapps.png
    :width: 600
    :alt: App split into three apps


Templates
=========

Araali baselines your application communication and presents them as an
identity-based policy recommendation which can then be accepted and converted
to policy. This means no handwriting policies, everything is automatically
discovered. Once these policies are accepted, they can also be enforced, which
means only whitelisted communication will be allowed and the rest will be
dropped. 

Policies can be accepted per application using Araali UI or APIs. This works
well for small to medium-sized applications but might seem tedious for a very
large app. Araali allows the option to automate the acceptance of policies by
leveraging templates. Templates are generally repeating patterns of
communication seen in an application. Some of the examples could be 

   a. Backend talking to Databases
   b. K8s nodes talking to control plane service
   c. VMs in the cloud talking to metadata services and so on
 
These repeatable and known communication patterns can be translated into
templates which helps with accepting the policies automatically without much
user intervention.

Creating Templates
------------------

Templates can be created using APIs/UI. Users can choose to create declarative
templates or convert an existing app’s policy links (suggested by Araali) to
templates

App Links to a Template
-----------------------


Araali UI
---------

In the image below the user chooses a link from Prometheus to the control plane
service and clicking on the green save button takes us to the template editor.

.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/linkToTemplatePrometheus.png
 :width: 600
 :alt: Araali UI link to template


In the editor the user can modify the selectors and it’s default values. This
will be used to filter links that the user wanted to automatically convert to
policies. The values specified here will be used in the policy selectors.


.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/linktoTemplatePrometheusTemplate.png
 :width: 600
 :alt: Araali UI link to template


Once the user is satisfied with the selectors, they can name the template and
also check the ‘Search and Use Continuously’ option at the bottom which will
allow the user to start using the template. The user can choose to just save
and turn on the template later as well.

APIs
----

List links
-----------

A user can use araalictl API to accomplish the link to template conversion
similar to the UI. The process starts by fetching links for a service or an app
lens. Below is an example of fetching links for service. The command returns a
list of links and the user picks out a link that they are interested in.

.. code-block::

    $ ./araalictl api -fetch-links -service 10.100.0.1:443 > prometheus_link

    - client:
        zone: mufasa-k8s
        app: monitoring.prometheus-operator.prometheus-operator
        process: operator
        binary_name: /bin/operator
        parent_process: containerd-shim
      server:
        subnet: 10.100.0.1
        netmask: 32
        dst_port: 443
        endpoint_group: __HOME__
      type: NAE
      state: BASELINE_ALERT
      timestamp: 1621886293000
      unique_id: id://mufasa-k8s,:monitoring.prometheus-operator.prometheus-operator:,operator,containerd-shim,/bin/operator+++10.100.0.1:443+++false+++false
      alert_info:
        communication_alert_type: LATERAL_MOVEMENT_ATTEMPTED
        process_alert_type: EXISTING_PROCESS_COMPROMISED
        reopen_count: 1
        status: OPEN
      rollup_ids:
      - id://mufasa-k8s,:monitoring.prometheus-operator.prometheus-operator:,operator,containerd-shim,/bin/operator+++10.100.0.1:443+++false+++false
      active_ports:
      - 443
    
Convert link to a template
----------------------------

Given the link above the user runs ‘link-to-template’ command to convert the
link to a template::

    $ cat prometheus_link | ./araalictl api -link-to-template

    - name: mufasa-k8s_monitoring.prometheus-operator.prometheus-operator_operator_to_10.100.0.1
      link_filter:
        client:
          zone: mufasa-k8s
          app: monitoring.prometheus-operator.prometheus-operator
          process: operator
        server:
          subnet: 10.100.0.1
          netmask: 32
          dst_port: 443
      use: false

If the user is satisfied with the above conversion they can accept it as is. If not, they can dump it to a file, edit, and then accept using the below command.

Accepting as is::

    $ cat <policy_yaml> | ./araalictl api -update-template -use-link-template

Accepting edited template::

    $ cat <edited_policy_yaml> | ./araalictl api -update-template


Declarative Templates
---------------------


Sometimes a user might have an in-depth understanding of their app and might
want to specify a declarative template. Some common examples, ‘snapd’ process
on AWS EC2s talking to the  Metadata Service (169.254.169.254:80), or the
Kubelet talking to the coreDNS in a Kubernetes cluster.


via UI
------


Go to the template page and click on the "green plus button" to add a new template.

.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/linktoTemplateAraaliTemplates.png
 :width: 600
 :alt: Araali Templates

Once the template editor pops up, the user can choose the selectors they would
like to use to filter links and accept them as policies (e.g., snapd talking to
the MetaData Service below). Once satisfied, name the template, and check the
option to “Search and use continuously” if they want to start using it right
away. The user can choose to just save and turn on the template later as well.

.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/linkToTemplateCreateTemplate.png
 :width: 600
 :alt: Create Templates


via Araali APIs
---------------


The Araali APIs can take declarative policies in yaml format. Below is a sample
yaml file::

    $ cat meta.meta
    - action: DEL
      name: amazonSsmAgentToMetadata
      link_filter:
        client:
          binary_name: /snap/amazon-ssm-agent/[0-9]+/amazon-ssm-agent
        server:
          subnet: 169.254.169.254
          netmask: 32
          dst_port: 80
      selector_change:
        client:
          binary_name: ^/snap/amazon-ssm-agent/[0-9]+/amazon-ssm-agent$
      use: true
    - name: ingressHaproxy
      link_filter:
        client:
          subnet: 0.0.0.0
        server:
          process: haproxy
          binary_name: /usr/sbin/haproxy
      use: true
    - name: snapdToSnapcraft
      link_filter:
        client:
          binary_name: /snap/core/.*/usr/lib/snapd/snapd
        server:
          dns_pattern: snapcraft.io|snapcraftcontent.com
          dst_port: 443
      selector_change:
        client:
          binary_name: ^/snap/core/.*/usr/lib/snapd/snapd$
      use: true
    - name: ssmAgentWorkerToMetadata
      link_filter:
        client:
          binary_name: /snap/amazon-ssm-agent/[0-9]+/ssm-agent-worker
        server:
          subnet: 169.254.169.254
          netmask: 32
          dst_port: 80
      selector_change:
        client:
          binary_name: ^/snap/amazon-ssm-agent/[0-9]+/ssm-agent-worker$
      use: true
    - name: kubeletToCoredns
      link_filter:
        client:
          zone: myk8s
          app: myapp
          binary_name: /snap/microk8s/\.*/kubelet
        server:
          zone: myk8s
          app: kube-system.coredns.coredns
          process: coredns
      selector_change:
        client:
          binary_name: /snap/microk8s/\.*/kubelet


There are three examples in the above yaml file.

1. ``amazonSsmAgentToMetadata`` - this is a non araali egress template.
   Non-araali servers are identified using dns_pattern or subnet/mask along
   with dst_port. This also shows an example of how to delete an existing
   template.

   This policy has an action as well and it is set to DEL, this helps with
   deleting templates that are already defined.

   ``snapdToSnapcraft`` - this is another example of non araali egress template
   where we are trying to match multiple fqdn patterns in link filter and
   trying to accept the links matching them.

2. ``ingressHaproxy`` - this is a non-araali ingress template. The non araali
   clients are identified using subnet and mask and if 0.0.0.0 is used  it
   needs to have an endpoint group marker __WORLD__ or __HOME__ to narrow them
   down to public or private ip addresses. If not specified, the template will
   match both. In this example we have skipped using it.

3. ``kubeletToCoredns`` - this is an araali to araali template. The link_filter
   section has client and server selectors defined to select links that need to
   be accepted as defined policy. Once the links are selected, we use selectors
   from the link to create policies by default. If we need those selectors to
   be replaced by a different value, we can specify them in the
   ``selector_change`` section. In this example we want the binary_name
   selector to be replaced with the regex ``/snap/microk8s/.*/kubelet.``

**Note:** Allowed selectors for Araali and Non-Araali endpoints.

**Araali** - "zone, app, process, binary_name, parent_process, dst_port"

**Non-Araali Client** - "subnet, netmask, endpoint group"

**Non-Araali Server** - "dns_pattern/(subnet, netmask), dst_port"

**Note:** Once defined, we need to start using the templates to accept links as defined policies. In the yaml we can set **use: true** like we have in ssm-agent-worker


API command to create templates::

    $ cat <policy_yaml> | ./araalictl api -update-template


Using Templates
---------------

Defining templates only store it in the data store. In order to use it, to
accept policies, a user has to set use boolean to true in the above yaml.
Another way to use the template is to issue the start command with an explicit
template name as shown below::

    ./araalictl api -template ingressHaproxy,snapdToSnapcraft -op use
   
**Stop using Templates**

.. code-block::

    ./araalictl api -template ingressHaproxy,snapdToSnapcraft -op stop
    
**Deleting Templates**

.. code-block::

    ./araalictl api -template ingressHaproxy,snapdToSnapcraft -op del

**Listing Templates**

.. code-block::

    ./araalictl api -list-template

The above command dumps the existing policies and their state in yaml format.


Alert Subscription (Email)
--------------------------

A user can subscribe to alert notifications. Anytime, a new alert is seen by
the system an email will be generated. With time as the app is discovered, new
alerts should reduce (only infrequent communications will trigger new alerts).

Security Professionals can subscribe for all alerts related to perimeter egress
or ingress across all apps.

Tenant Level for Perimeter Monitoring
-------------------------------------

Subscribing to Perimeter Egress::

     ./araalictl api -subscribe-for-alert -direction egress_world
       
**Options for direction are:** ingress_world|egress_world|ingress_home|egress_home|araali


Unsubscribing completely::

    ./araalictl api -unsubscribe-from-alert

