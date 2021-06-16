======================================
Getting Started with SIEM Integration
======================================

This is a guide on how to integrate Araali with supported SIEM products

Install Araali 
**************
Follow the instructions in the `getting started post <https://araali-networks-api.readthedocs.io/en/latest/gettingstarted.html#>`_

This sets up and authorizes Araalictl for local use.

Integration with ElasticStack
*****************************

Configure the TCP input plugin to accept json data. Open the existing LogStash config file
and add the following to the input plugin list.::

      input {
        tcp {
          port => 9099
          codec => "json"
        }
      }

Restart the LogStash service for the configuration to take effect.

   ``sudo systemctl restart logstash``

Check netstat to make sure LogStash has started listening on the chosen port.

   ``sudo netstat -lntp | grep 9099``

Start Araali Collector
**********************

Start the Araali Collector to submit Araali data to the configured LogStash TCP input port.

   ``./araalictl api -stream-start -stream-tcp=0.0.0.0:9099 -out=json -stream-cnt=1000``

Check status

   ``./araalictl api -stream-status``

