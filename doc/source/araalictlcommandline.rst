Command Line Guide
==================

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
