import datetime
import requests

from . import utils

g_debug = False

class API:
    def __init__(self):
        if utils.cfg["token"] is None:
            raise Exception("*** ARAALI_API_TOKEN environment variable is not set")

        self.host = "https://api-%s.aws.araalinetworks.com" % utils.cfg["backend"]
        self.headers = {"Authorization": "Bearer %s" % utils.cfg["token"]}

    def get(self, endpoint, data):
        if g_debug: print(self.host, self.headers, endpoint)
        rc = requests.get("%s/%s" % (self.host, endpoint), params=data, headers=self.headers)
        if g_debug: print(rc.request.url)
        if rc.status_code != 200:
            print("*** REST api error: %s" % rc.status_code)
        return rc.json(), 0 if rc.status_code == 200 else rc.status_code

    def get_alerts(self, count=None, ago=None, token=None, tenant=None):
        """Fetches alerts
            Usage: alerts, next_page, status = api.get_alerts()
        """
        data = {
                "filter.openAlerts": True,
                "filter.closedAlerts": False,
                "filter.listAllAlerts": False,
                "filter.perimeterIngress": True,
                "filter.perimeterEgress": True,
                "filter.homeNonAraaliIngress": True,
                "filter.homeNonAraaliEgress": True,
                "filter.araaliToAraali": True,
        }
        if tenant is None:
            if utils.cfg["tenant"]: data["tenant.id"] = utils.cfg["tenant"]
        else:
            data["tenant.id"] = tenant

        if not ago:
            ago = "infinite"
        if ago != "infinite":
            ago = dict([utils.make_map(a) for a in ago.split(",")])
            data["filter.time.startTime"] = (datetime.datetime.utcnow() - datetime.timedelta(**ago)).strftime('%Y-%m-%dT%H:%M:%SZ')
            data["filter.time.endTime"] = (datetime.datetime.utcnow()).strftime('%Y-%m-%dT%H:%M:%SZ')

        if count is None: count = 1000
        data["count"] = count

        if token: data["pagingToken"] = token
        if g_debug: print(data)

        ret, status = self.get("api/v2/listAlerts", data)
        return ret.get("links", []), ret.get("paging_token", None), status

    def get_assets(self, zone=None, app=None, ago=None, tenant=None):
        """Fetches assets
            Usage: assets, status = api.get_assets()
        """
        data = {
                "filter.listActiveVm": True,
                "filter.listInactiveVm": False,
                "filter.listActiveContainer": True,
                "filter.listInactiveContainer": False,
        }
        if tenant is None:
            if utils.cfg["tenant"]: data["tenant.id"] = utils.cfg["tenant"]
        else:
            data["tenant.id"] = tenant
        
        if zone: data["zone"] = zone
        if app: data["app"] = app

        if not ago:
            ago = "days=1"
        ago = dict([utils.make_map(a) for a in ago.split(",")])
        data["time.startTime"] = (datetime.datetime.utcnow() - datetime.timedelta(**ago)).strftime('%Y-%m-%dT%H:%M:%SZ')
        data["time.endTime"] = (datetime.datetime.utcnow()).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        if g_debug: print(data)

        ret, status = self.get("api/v2/listAssets", data)
        return ret.get("assets", []), status

    def get_links(self, zone=None, app=None, svc=None, ago=None, tenant=None):
        """Fetches links
            Usage: links, status = api.get_links()
        """
        data = {}
        if tenant is None:
            if utils.cfg["tenant"]: data["tenant.id"] = utils.cfg["tenant"]
        else:
            data["tenant.id"] = tenant
        if zone: data["zone"] = zone
        if app: data["app"] = app
        if svc: data["service"] = svc

        if not ago:
            ago = "days=1"
        ago = dict([utils.make_map(a) for a in ago.split(",")])
        data["time.startTime"] = (datetime.datetime.utcnow() - datetime.timedelta(**ago)).strftime('%Y-%m-%dT%H:%M:%SZ')
        data["time.endTime"] = (datetime.datetime.utcnow()).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        if g_debug: print(data)

        ret, status = self.get("api/v2/listLinks", data)
        return ret.get("links", []), status

    def get_insights(self, zone=None, tenant=None):
        """Fetches insights
            Usage: insights, status = api.get_insights()
        """
        data = {}
        if tenant is None:
            if utils.cfg["tenant"]: data["tenant.id"] = utils.cfg["tenant"]
        else:
            data["tenant.id"] = tenant
        if zone: data["zone"] = zone
        
        if g_debug: print(data)

        ret, status = self.get("api/v2/listInsights", data)
        return ret["insights"], status
