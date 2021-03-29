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

  -upgrade
    	manually upgrade to latest, without re-authorizing

assessment
----------
./araalictl assessment
        Used to start and stop point in time assessments

-start          start the assessment
-stop           stop the assessment
-report         get a report on findings

version
-------
./araalictl version
        Used to get the version of araalictl

-v	        verbose
