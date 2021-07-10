Command Line Doc
================

token
-----
./araalictl token
   Generate token for api use (programmatic access)

authorize
---------
sudo ./araalictl authorize
        Used to authorize this copy of araalictl.

        Without any arguments, it will initiate the authorization and also
        auto-upgrade to the latest published production version.

  -check
        check authorization status

  -clean
        clean up and logout

  -token <fname>
         Use fname for token based auth. If - is used for fname, token is
         expected to be piped through stdin

         Usage::

            # generate a token for api use
            TOKEN=$(./araalictl token)

            # usually TOKEN is generated elsewhere and injected with env vars
            echo $TOKEN | sudo ./araalictl authorize -token=-

assessment
----------
./araalictl assessment
        Used to start and stop point in time assessments

-start          start the assessment
-stop           stop the assessment
-report         get a report on findings
-ignoreMK8S     ignore MicroK8S even if present

version
-------
./araalictl version
        Used to get the version of araalictl

-v	        verbose

upgrade
-------
sudo ./araalictl upgrade
        Upgrade araalictl to the latest version available.

api
----
./araalictl api
        Used to access the api

-h          get a list of commands

lens
____
-fetch-enforcement-status                   show all lenses
    -enforced                               show enforced lenses

-fetch-starred-lens                         show starred lenses

-clear-starred-lens                         unstar all lenses

-zone zone_name -app app_name -star-lens    star zone-app lens

-service fqdn/ip:port -star-lens            star service lens

**enforce**

 ::

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


unenforce
    follow the steps outlined to enforce but change ``bool`` values to ``False`` and ``"ENABLED"``` to ``"DISABLED"``