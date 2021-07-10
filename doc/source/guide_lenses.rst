Guide to Lenses
===============

Overview
--------

A Lens can be either a zone-app or a service.
They are modular and comprehensive units that help to focus on smaller sections of the workspace.

Functions
---------

Get
***

Get all Lenses. Can be filtered based on enforcement and starred status.

.. tabs::
   .. code-tab:: bash Command Line

         ./araalictl api -fetch-enforcement-status
         # "-enforced" tag optional
         ./araalictl api -fetch-starred-lens

   .. code-tab:: py

         api.Lens.get(enforced, starred)
         # enforced: default=False
         # starred: default=False

Unstar
******

Unstar all currently starred lenses.

.. tabs::
   .. code-tab:: bash Command Line

         ./araalictl api -clear-starred-lens

   .. code-tab:: py

         api.Lens.unstar_all()

Star
****

Star Lens.

.. tabs::
   .. code-tab:: bash Command Line

         ./araalictl api -zone zone_name -app app_name -star-lens
         # star zone-app lens
         ./araalictl api -service fqdn/ip:port -star-lens
         # star service lens

   .. code-tab:: py

         .star()

Enforce
*******

Enforce lens.

.. tabs::
   .. code-tab:: bash Command Line

        vi enforce_za.txt
        # "i" to insert at cursor, "a" for after cursor, and "o" for line above cursor
        # input the following
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
        # Esc to edit exit mode
        # “:wq”
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

Unenforce lens.

.. tabs::
   .. code-tab:: bash Command Line

         # follow steps for enforce
         # but change True values to False
         # and "ENABLED" to "DISABLED"

   .. code-tab:: py

         .unenforce(za_ingress, za_egress, za_internal, svc_ingress)
         # za_ingress: default=False
         # za_egress: default=False
         # za_internal: default=False
         # svc_ingress: default=False
