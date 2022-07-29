"""araali package provides API access for python

    Setup (one time):
        # setup a python3 virtualenv to run araali                                      
        cd ~/
        python3 -m venv araaliapienv                                                    
        source araaliapienv/bin/activate                                                
        pip install araali

    Every other time (enter the virtualenv and use it):
        cd ~/
        source araaliapienv/bin/activate                                                
        pip install --upgrade araali

    Usage:
        # export your api token

        export ARAALI_API_TOKEN="<your-token-here>"

        # from python REPL

            >>> import araali                                                               
            >>> help(araali)   

        # from your code

            import araali
            api = araali.API()

            ###
            # alerts
            #   - count is a limit on how many alerts to fetch
            #   - ago is a string, specifying lookback in days, hours, or minutes
            #       eg: ago="days=10,hours=5" etc.
            #   - default for ago is "inifinte" (beginning of life)
            #   - both parameters are optional
            ###
            alerts, page, status = api.get_alerts(count, ago)
            if status == 0:
                print("Got %s alerts" % len(alerts))
                araali.utils.dump_table(alerts)

            ###
            # assets and CVEs
            #   - all args are optional
            #   - you can limit assets in a zone or a (zone,app)
            ###
            assets, status = api.get_assets(zone, app, ago)
            if status == 0:
                araali.utils.dump_table(assets)

            ###
            # polices for apps and services
            #   - either (zone, app) or svc needs to be specified
            #       e.g.: svc="169.254.169.254:80"
            ###
            links, status = api.get_links(zone, app, svc, ago)
            if status == 0:
                araali.utils.dump_table(links)

            ###
            # insights
            #   - zone is optional and can be used to limit insights for a zone
            ###
            insights, status = api.get_insights(zone)
            if status == 0:
                araali.utils.dump_table(insights)

        # The module can also be run from the command line

            python -m pydoc araali                                                          
            python -m araali -h
"""

from . import utils
if utils.cfg["token"]:
    from .api import API
else:
    from .araalictl import API
