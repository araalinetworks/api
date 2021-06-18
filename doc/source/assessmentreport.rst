===============================
Understanding Araali Assessment
===============================

In this section, we’ll walk you through the key security insights uncovered
by Araali assessment. Much of the information can also be obtained as a yaml
report, but the CVE annotation is available only on Araali UI.

1) Overall count of services in your environment categorized as - publicly
   accessible, internal only, and in use external services
2) Important services / datastores (**DBs and DBaaS**) that you might want to
   protect with zero-trust
3) Test for important services being **accessible by intruders**?
4) **Inactive listen ports** found in the environment
5) Report of vulnerable VMs and Containers (UI only)

**How can you use this information:** 

First and foremost, it produces a comprehensive, layered diagram of your
environment and shows all the active apps and services.

This information helps you understand if you have any security misconfiguration
in your environment; for example, your DB might be accidentally exposed to the
world or accessible by intruders within your environment (lack of access
controls).

Similarly, intruders might have access to your credential stores and in
particular the metadata service, which holds keys to access cloud resources
(CapitalOne Breach, 2019).

Also, it allows you to monitor your software supply chain - we call it
monitoring your monitors.

Finally, you can visualize the flow of data between applications in your
environment, annotated by any unpatched vulnerabilities, to help identify risk
and prioritize potential remediation efforts.


Yaml output
"""""""""""

You can generate the sample report using::

      ./araalictl assessment -report

The report has many sections that are laid out in the diagrams below.

The top part of the report is the summary for the cluster.

1. Number of zones (or kubernetes clusters) = 1
2. Number of apps (or kubernetes namespaces) = 6
3. Number of internal services (not publicly visible) = 24
4. Number of external services consumed = 27
5. Number of services provided (publicly exposed) = 29


.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/araalireportsummary.png
 :width: 650
 :alt: Araali Report Summary

**Database** in your stack are listed under "databases" or "dbaas," if you are
running the database as a service. Depending on the database or dbaas you can
see the name of the process or port and also if the **database is accessible
from an outside pod.** If your db has unnecessary exposure, you will see the
**flag is_accessible as true**.

**Top consumed services** are a list of external services/egress going out of
your environment. 

**Inactive port services** are services that have open ports that are **not
being used during the assessment**. We encourage you to verify and close these
ports if not in use.


.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/araalireportdetail1.png
 :width: 650
 :alt: Araali Report Details

**Internet exposed services** are your services that are world visible or
exposed on the internet. Any misconfiguration that leads to internet exposure
will show up here.

**Geo org accessors** are services that access external/3rd party services
organized by organization name and country.

**Starred Lens** is a list of important services and apps - your apps running
Databases or services that have a high number of connections. They are
auto-discovered and starred and will also show up on your Dashboard page.

.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/araalireportdetail2.png
 :width: 650
 :alt: Araali Report Details


Navigating via the UI
"""""""""""""""""""""

You can `log into <https://console.araalinetworks.com>`_ the UI to get visual
information on your cluster, created out of the box by Araali. You start with a
**dashboard** which is similar to the yaml file summary and gives you a
high-level count of services and compute and auto-starred apps, pinned on the
top part of the UI.

.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/UIdashboardwithstarred.png
 :width: 650
 :alt: Araali Dashboard with Starred Apps

You can drill into your cluster by clicking on **Runtime** or **Zones**. On the
zones page, you will get a high-level view of your cluster. The left hand is
the ingress and the right hand is the egress made from your cluster. If you
have internet exposure, you will see a world map on the left-hand column.
Similarly, if you have a sneaky command and control, it will show up on the
right-hand side. 

.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/UIdevZone.png
 :width: 650
 :alt: Araali Dashboard with Starred Apps

You can further drill into your cluster to get to the **namespace view** by
clicking on the magnifying glass in the cluster's card.

You can see all the namespaces listed out here with both ingress and egress
connections clearly listed out.

.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/UIdevzoneapp.png
 :width: 650
 :alt: Araali Dashboard with Starred Apps


You can further drill inside any namespace by clicking on the magnifying glass.
We will go to the **strutfrontend** namespace. Inside the namespace, you can
see all the processes running as part of that namespace. If you have a database
it will show up in the middle row as a card, if you have a dbaas it will show
up in the egress column. In the example here we have a process with just
ingress and no egress. The process also has inactive ports matching what we saw
in the yaml file.


.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/UIAlertRedstrut.png
 :width: 650
 :alt: Araali Dashboard with Starred Apps

We encourage you to go through all the namespaces and verify your apps,
especially if it has a database or if it is using a database as a service.
