Guide to Lenses
===============

Overview
--------

Securing everything is a euphemism for securing nothing, or at best doing best-effort security.

Instead, confidently and precisely secure what matters, even in the light of an intruder within the premises.
Zero Trust performs security the way the Secret Service protects the President of the United States. At any point,
they need to know who the President is, where they are at all times, and who has access to them at all times.
It's about identifying the protect surface, lensing concern, and creating focus.

Lenses are the minimum yet completely self-contained units that can be owned, reviewed, monitored, and enforced.
They can either be applications that Araali protects, or services that are used by Araali-protected clients.
By lensing concern, it is possible get to focus on one app or service at a time, wherever the concern may lie.

Turning enforcement on for an Araali-protected app means that only authorized clients can use the services
offered by the app (ingress). Should the app be compromised by an intruder, it won't pollute the
environment or move laterally (egress), or even gain access to services that are internal to the app (internal).

Turning enforcement on for a service lens means that only approved apps from all Araali-protected assets
can ever access the service. If there is an intruder within the Araali-protected environment,
it doesn't get the same access to the service, as your own legitimate apps would. A service, by definition, is
third-party, and Araali does not have presence in it. Therefore, the enforcement happens on the client side, and
it makes sure that only the correct identities get to access an external service from within your environment.

But before getting into enforcement, it is important to first identity what lenses are worth spending time on.
It is possible to pin important lenses to the dashboard, check the enforcement status, and toggle enforcement on or off
using the APIs.

Functions
---------

Get
***

Get all Lenses. It is possible to optionally get only enforced lenses or only starred lenses.

.. tabs::
   .. code-tab:: sh Command Line

        # get all lenses along with their enforcement status
        ./araalictl api -fetch-enforcement-status

        # use -enforced flag to fetch only enforced lenses
        ./araalictl api -fetch-enforcement-status -enforced

        # use a seperate command to fetch only starred lenses
        ./araalictl api -fetch-starred-lens

   .. code-tab:: py

        # Without params it will get all lenses
        # Use enforced=True, or starred=True explictly to get the subset that
        # is enforced/starred
        api.Lens.get(enforced=True, starred=True)

Star
****

Star Lens.

.. tabs::
   .. code-tab:: sh Command Line

        # star zone-app lens
        ./araalictl api -zone zone_name -app app_name -star-lens

        # star service lens
        ./araalictl api -service fqdn/ip:port -star-lens

   .. code-tab:: py

        .star()

Unstar
******

Unstar all currently starred Lenses. It is like performing a factory reset and clearing the Araali dashboard.

.. tabs::
   .. code-tab:: sh Command Line

        ./araalictl api -clear-starred-lens

   .. code-tab:: py

        api.Lens.unstar_all()

Monitor
*******

Monitor a lens. You start getting emails when there is new activity in the lens

.. tabs::
   .. code-tab:: sh Command Line

        # subscribe to zone-app lens alerts
        ./araalictl api -zone zone_name -app app_name -subscribe-for-alert

        # subscribe to service lens alerts
        ./araalictl api -service fqdn/ip:port -subscribe-for-alert

        # subscribe to directional alerts
        ./araalictl api -subscribe-for-alert -direction ingress_world, egress_world

   .. code-tab:: py

        .monitor(email=None)

Unmonitor
*********

Stop monitoring a lens. You stop getting emails for the lens

.. tabs::
   .. code-tab:: sh Command Line

        # unsubscribe from zone-app lens alerts
        ./araalictl api -zone zone_name -app app_name -unsubscribe-from-alert

        # unsubscribe from service lens alerts
        ./araalictl api -service fqdn/ip:port -unsubscribe-from-alert

   .. code-tab:: py

         .unmonitor(email=None)


Monitor All
***********

Monitor all lenses for alerts. You start getting emails when there are new alerts.

.. tabs::
   .. code-tab:: sh Command Line

        # subscribe to world alerts
        ./araalictl api -subscribe-for-alert -direction ingress_world, egress_world


   .. code-tab:: py

         api.Lens.monitor_world()


Unmonitor All
***********

Unmonitor all lenses for alerts. You will stop getting emails when there are new alerts.

.. tabs::
   .. code-tab:: sh Command Line

        # unsubscribe from world alerts
        ./araalictl api -unsubscribe-from-alert -direction ingress_world, egress_world


   .. code-tab:: py

         api.Lens.unmonitor_world()



Enforce
*******

Enforce Lens.

.. tabs::
   .. code-tab:: sh Command Line

        # "i" to insert at cursor, "a" for after cursor, and "o" for line above cursor
        # input the following
        vi enforce_za.txt

        # for zone-app:
        - zone_name: string
          apps:
          - app_name: string
            ingress_enforced: True
            egress_enforced: True
            internal_enforced: True

        # for service:
        - dns_pattern: fqdn/ip
          dst_port: port
          new_enforcement_state: ENABLED

        # Esc to exit edit mode in vi
        # “:wq” to quit once in control mode

        # for zone-app
        cat enforce_za.txt | ./araalictl api -enforce-zone-app

        # for service
        cat enforce_za.txt | ./araalictl api -enforce-service

   .. code-tab:: py

         .enforce(za_ingress, za_egress, za_internal, svc_ingress)
         # za_ingress: default=True
         # za_egress: default=True
         # za_internal: default=False
         # svc_ingress: default=True

Unenforce
*********

Unenforce Lens.

.. tabs::
   .. code-tab:: sh Command Line

         # follow steps for enforce
         # but change True values to False
         # and "ENABLED" to "DISABLED"

   .. code-tab:: py

         .unenforce(za_ingress, za_egress, za_internal, svc_ingress)
         # za_ingress: default=False
         # za_egress: default=False
         # za_internal: default=False
         # svc_ingress: default=False
