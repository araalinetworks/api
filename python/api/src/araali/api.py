from __future__ import print_function

import datetime
import requests
import json

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

    def post(self, endpoint, data):
        self.headers["Content-Type"] = "application/json"
        if g_debug:
            print(self.host, self.headers, endpoint)

        rc = requests.post("%s/%s" % (self.host, endpoint),
                           data=data, headers=self.headers)
        if g_debug:
            print(rc.request.url)
            print(rc.json())
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

    def get_fw_config(self, zone, tenant=None):
        """Fetches firewall knobs enabled for a tenant in the zone
            Usage: knobs, status = api.get_fw_config()
        """
        data = {}
        if tenant is None:
            if utils.cfg["tenant"]:
                data["tenant_id"] = utils.cfg["tenant"]
        else:
            data["tenant_id"] = tenant
        data["zone"] = zone

        if g_debug:
            print(data)

        ret, status = self.get("api/v2/getFirewallConfig", data)
        if status == 0:
            return ret["knobs"]
        return None

    def update_fw_config(self, zone, tenant=None, data_file_location=None):
        """Update firewall knobs for a tenant in the zone
            Usage: status = api.update_fw_config()
        """

        json_file_location = "/tmp/fw_cfg.json"
        if data_file_location:
            json_file_location = data_file_location

        json_data = {}
        try:
            with open(json_file_location) as json_file:
                json_data = json.load(json_file)
        except Exception as ex:
            print(ex)
            return "exception parsing json"

        if g_debug:
            print(json_data)

        data = {}
        if tenant is None:
            if utils.cfg["tenant"]:
                data["tenant_id"] = utils.cfg["tenant"]
        else:
            data["tenant_id"] = tenant
        data["zone"] = zone
        data["knobs"] = json_data

        json_dump = json.dumps(data, indent=4)

        if g_debug:
            print(data)
            print(json_dump)

        ret, status = self.post("api/v2/updateFirewallConfig", json_dump)
        return status

    def get_helm_values(self, workload_name, nanny=None, tenant=None):
        """Fetches helm values for nanny/controller or firewall chart
            Usage: values_yaml = api.get_helm_values()
        """
        data = {}
        if tenant is None:
            if utils.cfg["tenant"]:
                data["tenant.id"] = utils.cfg["tenant"]
        else:
            data["tenant.id"] = tenant
        data["workload_name"] = workload_name

        if nanny is None:
            data["yaml_type"] = "1"
        else:
            data["yaml_type"] = "2"

        if g_debug:
            print(data)

        ret, status = self.get("api/v2/createFortifyYaml", data)
        if g_debug:
            print(ret)

        if "code" in ret["response"] and ret["response"]["code"] != 0:
            print("error ", ret["response"]["message"])
            return ""

        return ret["workload_yaml"]
