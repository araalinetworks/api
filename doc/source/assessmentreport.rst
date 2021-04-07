===================================
Understanding the Assessment Report
===================================

In this section, we’ll walk you through the key security questions answered by the assessment report.

1) What are my apps and services - providers, consumers, and internal
2) What and where are the DBs and DBaaS running
3) Inactive listen to ports
4) Is my DB and Metadata service accessible from other services
5) Vulnerable VMs and Containers (UI)

**How can you use this information:** 

First and foremost, it produces an architecture diagram of your application and shows all the active databases and apps.

This information helps you understand if you have any misconfiguration in your system; for example, DB is exposed to the world or accessible from unauthorized services. Or if your Database is accessible from multiple pods in your Kubernetes cluster leading to increased risk.

Similarly, can services access your metadata service, which holds keys to your kingdom (exploited in CapitalOne hack). Also, it allows you to monitor any third-party apps or services in your environment - we call it monitoring your monitors or circular responsibility.

Finally, we give you a process-level inventory that you could use to prioritize your vulnerabilities. 


Yaml output
"""""""""""

You can generate the sample report using::

      ./araalictl assessment -report

The report has many sections that are laid out in the diagrams below.

The top part of the report is the summary for the cluster.

1. Number of zone/cluster = 1
2. Number of apps/namespace = 6
3. Number of services internal to the namespace = 24
4. Number of services consumed/egress = 27
5. Number of services provided/ingress = 29


.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/araalireportsummary.png
 :width: 650
 :alt: Araali Report Summary

**Database** in your stack are listed under "databases" or "dbaas," if you are running the database as a service. Depending on the database or dbaas you can see the name of the process or port and also if the database is accessible from an outside pod.

**Top consumed services** are a list of external services/egress going out of your environment. 

**Inactive port services** are services that have open ports that are **not being used during the assessment**. We encourage you to verify and close these ports if not in use.


.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/araalireportdetail1.png
 :width: 650
 :alt: Araali Report Details

**Internet exposed services** are your services that are world visible or exposed on the internet. Any misconfiguration that leads to internet exposure will show up here.

**Geo org accessors** are services that access external/3rd party services organized by organization name and country.

**Starred Lens** is a list of important services and apps - your apps running Databases or services that have a high number of connections. They are auto-discovered and starred and will also show up on your Dashboard page.

.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/araalireportdetail2.png
 :width: 650
 :alt: Araali Report Details




Navigating via the UI
"""""""""""""""""""""


You can `log <https://console.araalinetworks.com>`_ into the UI to get visual information on your cluster, created out of the box by Araali. You start with a **dashboard** which is similar to the yaml file summary and gives you a high-level count of services and compute and auto-starred apps, pinned on the top part of the UI.


.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/UIdashboardwithstarred.png
 :width: 650
 :alt: Araali Dashboard with Starred Apps

You can drill into your cluster by clicking on **Runtime** or **Zones**. On the zones page, you will get a high-level view of your cluster. The left hand is the ingress and the right hand is the egress made from your cluster. If you have internet exposure, you will see a world map on the left-hand column. Similarly, if you have a sneaky command and control, it will show up on the right-hand side. 


.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/UIdevZone.png
 :width: 650
 :alt: Araali Dashboard with Starred Apps

You can further drill into your cluster to get to the **namespace view** by clicking on the magnifying glass in the cluster's card.

You can see all the namespaces listed out here with both ingress and egress connections clearly listed out.

.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/UIdevzoneapp.png
 :width: 650
 :alt: Araali Dashboard with Starred Apps


You can further drill inside any namespace by clicking on the magnifying glass. We will go to the **strutfrontend** namespace. Inside the namespace, you can see all the processes running as part of that namespace. If you have a database it will show up in the middle row as a card, if you have a dbaas it will show up in the egress column. In the example here we have a process with just ingress and no egress. The process also has inactive ports matching what we saw in the yaml file.


.. image:: https://raw.githubusercontent.com/araalinetworks/api/main/doc/source/images/UIAlertRedstrut.png
 :width: 650
 :alt: Araali Dashboard with Starred Apps

We encourage you to go through all the namespaces and verify your apps, especially if it has a database or if it is using a database as a service.
