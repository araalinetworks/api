Python API Doc
==============
Setup
-----
.. function:: api.auth(token)

   authorize araalictl for api use. This operation is idempotent and can be run
   multiple times without any side effect App.

   :param token: token is generated from a manually authenticated araalictl
   :type token: string

.. function:: api.deauth()

   deauth araalictl from this node.

.. function:: api.set_araalictl_path(new_path)

   set the location of araalictl on this node.

   :param new_path: araalictl path
   :type new_path: string

App
---
.. class:: api.App

   A class representing an application

   Usage:

      >>> import api
      >>> app = api.App("nightly", "bendvm")
      >>> for link in app.iterlinks():
      ...    link.accept()
      ...
      >>> app.review()
      >>> app.commit()

   :param zone: name of the zone
   :type zone: string
   :param app: name of the app
   :type app: string

   .. function:: iterlinks()

      An iterator for all links of the app
      
      :rtype: iterator of api.Link

   .. function:: review()

      Review edits made to links in the app. Links can be accepted or snoozed.

   .. function:: commit()

      Commit changes made to links in the app.

Link
----
.. class:: api.Link

   Class representing an individual link (policy suggestion). Links can be
   accepted or snoozed. Accepted links become whitelist policies for the app,
   while snoozed links will appear again if new flows are observed.

   Usage:

      >>> for link in app.iterlinks():
      ...    link.accept()
      ...

   .. function:: accept()
      :noindex:

      Accept link as whitelisted policy.

   .. function:: snooze()
      :noindex:

      Snooze link. A snoozed link is forgotten. It will show up again if a new
      flow is observed. Typically links are snoozed when the underlying problem
      is addressed. It is snoozed so that there is notification on subsequent
      occurance.

LinkTable
---------
.. class:: class api.LinkTable

   Class representing an arbitrary table/collection of links (policies), that
   allows action on multiple links at the same time. Links can be filtered at
   init, so only filtered links enter the table.
   
   Subsequently action can be taken on all links in the filtered table, or by
   specifying specific indices.  Links can be committed back on a per app basis
   or for the entire runtime (which essentially iterates over every app in the
   runtime).

   Usage:

      >>> links = api.LinkTable(app.iterlinks())
      >>> links = links.accept(0,2)
      >>> app.review()
      >>> app.commit()


   :param links: a list of link objects
   :type links: list of api.Link
   :param \*filters: filter to be applied on the input (of links). An arbitrary number of filters can be specified. There are some predefined filters in the api for common use: api.f.*
   :type \*filters: lambda returning boolean

   .. function:: accept(* args)

      Accept link by index number. If no index is provided, all links in the
      table will be accepted.

      :param args: Multiple indices can be passed
      :type args: any number of int's

   .. function:: snooze(* args)

      Snooze link by index number. If no index is provided, all links in the
      table will be snoozed.

      :param args: Multiple indices can be passed
      :type args: any number of int's
