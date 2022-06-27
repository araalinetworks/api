Golang API V1
=============

Setup
-----
.. function:: araalictl.SetAraalictlPath(newPath)

   set the location of araalictl on this node.

   :param newPath: araalictl path
   :type newPath: string

.. function:: araalictl.Authorize(token)

   authorize araalictl for api use. This operation is idempotent and can be run
   multiple times without any side effect App.

   :param token: token is generated from a manually authenticated araalictl
   :type token: string

.. function:: araalictl.DeAuthorize()

   deauth araalictl from this node.

App
---
.. class:: araalictl.App

   A struct representing an application

   Usage::

        app := araalictl.App{ZoneName: "nightly", AppName: "bendvm"}
        app.Refresh()
        app.Links[0].Accept()
        app.Commit()

   :param ZoneName: name of the zone
   :type ZoneName: string
   :param AppName: name of the app
   :type AppName: string

   .. function:: Refresh()

      Fetches all the links for the app and links are accessible as app.Links.
      
   .. function:: Commit()

      Commit changes made to links in the app.

Link
----
.. class:: araalictl.Link

   Struct representing an individual link (policy suggestion). Links can be
   accepted, denied or snoozed. Accepted links become whitelist policies for the app,
   denied links help with ignoring alerts until taken care of while snoozed links 
   will appear again if new flows are observed.

   Usage::

      app.Links[0].Accept()

      // or,
      app.Links[0].Snooze()

      // or,
      app.Links[0].Deny()

   .. function:: Accept()
      :noindex:

      Accept link as whitelisted policy.

   .. function:: Snooze()
      :noindex:

      Snooze link. A snoozed link is forgotten. It will show up again if a new
      flow is observed. Typically links are snoozed when the underlying problem
      is addressed. It is snoozed so that there is notification on subsequent
      occurrence.

   .. function:: Deny()
      :noindex:

      Deny link. A denied link is snoozed forever. You not only want to not
      accept it, but you dont even want to snooze because you are aware of it
      and dont want to accept it, ever!
