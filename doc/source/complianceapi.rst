Compliance via API
==================


Overview
--------
Araali also allows you to fulfill your SOC2 compliance requirements. Some of the areas where Araali can help fulfill the SOC2 compliance requirements are:

1. Visibility into your Assets - VMs and Containers
    * :ref:`get_compute()`

*The get_compute API is very rich and has information on both Assets as well as corresponding CVEs*

2. Vulnerability List based on your VMs and Containers
    * :ref:`get_compute()`

3. Compensating control for Vulnerability - Araali Shielding
    * :ref:`get_lenses(enforced=True)`

*In SOC2 you have to show compensating control for known vulnerability. Araali allows you to shield your vulnerable Apps or Containers to fulfill this obligation. This API gives a list of Zones and Apps that have been shielded/enforced.  Using this API with the output of get_compute(), you can understand which assets have been Araali Shielded.*

4. Alerts generated - Intrusion Detection
    * :ref:`get_alerts()`

*This API gives you a list of Alerts that were generated in a given period of time.*

5. Users who have access to Araali and their assigned Roles
    * :ref:`rbac_show_users()`

*This API gives a list of users along with their assigned role.*

6. Proactively Shielded Apps - Intrusion Prevention
    * :ref:`get_enforced_links()`

*Araali Shielding is similar to Application Firewall as it enforces both incoming and outgoing traffic from your assets. Once Shielded, Araali will not let your application deviate from these baseline policies making them unexploitable. These are enforced processes belong to a certain Zone/Cluster and App/Namespace which can be tabulated with this API.*


.. image:: images/compliance_diagram.png
 :alt: Compliance Diagram

For SOC2 Type2 compliance a customer has to show that **they have ongoing security controls in place and it can be proved via periodic capture of evidence.** To prove the above controls Araali can take periodic snapshots of all the items above, and put it in a report that can be used by the auditor.

Python Usage
************

1. Fork the open source `Github Repo<https://github.com/araalinetworks/api>`_
2. Download the fork to your local machine
3. Navigate to the fork through command line
4. Run Python in the command line

Commands
--------
To specify tenant through the command line, use the ``-t`` or ``--tenant`` flags. To do so through Python, use the ``tenant`` argument.

get_compute()
*************
Gets computes for a specific zone-app

.. tabs::
  .. code-tab:: sh Command Line

       ./araalictl api -zone <zone> -app <zone> -fetch-compute

  .. code-tab:: py

       import araalictl
       araalictl.get_compute(zone=<zone>, app=<app>)

get_lenses(enforced=True)
**********************
Gets all enforced lenses for the tenant (if specified)

.. tabs::
  .. code-tab:: sh Command Line

       ./araalictl api -fetch-enforcement-status -enforced

  .. code-tab:: py

       import araalictl
       araalictl.get_lenses(enforced=True)

get_alerts()
************
Gets all alerts for the tenant (if specified).

.. tabs::
  .. code-tab:: sh Command Line

       # use -starttime and -endtime to specify start and end times (epoch)
       ./araalictl api -fetch-alerts -paging-token <token> -count <count>

  .. code-tab:: py

       # use start_time and end_time to specify start and end times (epoch)
       import araalictl
       araalictl.get_alerts(token=<token>, count=<count>)

rbac_show_users()
*****************
Gets all current users for tenant (if specified)

.. tabs::
  .. code-tab:: sh Command Line

       ./araalictl user-role -op list-user-roles

  .. code-tab:: py

       import araalictl
       araalictl.rbac_show_users()

get_enforced_links()
********************
Gets enforced links for tenant (if specified)

.. tabs::
  .. code-tab:: sh Command Line

       # This command uses multiple other Python wrapper commands, making a command line execution difficult

  .. code-tab:: py

       import araalictl
       araalictl.get_enforced_links()
