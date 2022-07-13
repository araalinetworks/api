"""fake api using araalictl underneath
    api = api.API()

    alerts, page, status = api.get_alerts(args.count, args.ago)
    assets, status = api.get_assets(args.zone, args.app, args.ago)
    links, status = api.get_links(args.zone, args.app, args.svc, args.ago)
    insights, status = api.get_insights(args.zone)
"""
import datetime
import os
import platform
import sys
from . import utils
import yaml

g_debug = False

class API:
    def __init__(self):
        progdir = os.path.dirname(os.path.abspath(__file__))
        if os.path.isfile(progdir + "/bin/araalictl"):
            self.cmdline = progdir + "/bin/araalictl"
        else:
            self.cmdline = progdir + "/bin/" + {
                                                "Linux": "araalictl.linux-amd64",
                                                "Darwin": "araalictl.darwin-amd64"
                                               }[platform.system()]

    def get_alerts(self, count=None, ago=None, token=None, tenant=None):
        """get alerts"""

        if tenant is None: tenant = utils.cfg["tenant"]
        if count is None: count = 1000

        if not ago:
            start_time = 0
            end_time = 0
        else:
            ago = dict([utils.make_map(a) for a in ago.split(",")])
            start_time = datetime.datetime.now() - datetime.timedelta(**ago)
            end_time = datetime.datetime.now()

            start_time = int(start_time.timestamp())
            end_time = int(end_time.timestamp())
 
        cmd = "-starttime %s" % (start_time)
        cmd += " -endtime %s" % (end_time)
        if token:
            cmd += " -paging-token %s" % token

        tstr = " -tenant=%s " % (tenant) if tenant else ""
        rc = utils.run_command("%s api -fetch-alerts %s -count %s %s" % (
                            self.cmdline, cmd, count, tstr),
                         debug=g_debug, result=True, strip=False)
        assert rc[0] == 0, rc[1]

        token = None
        objs = yaml.load(rc[1], yaml.SafeLoader)
        if objs:
            token=objs[-1].get("paging_token", None)

        return objs, token, 0

    def get_assets(self, zone, app, ago):
        pass

    def get_links(self, zone, app, svc, ago):
        pass

    def get_insights(self, zone):
        pass
