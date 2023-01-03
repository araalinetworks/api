from __future__ import print_function

import datetime
import requests
import json
import yaml

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
        if g_debug: print(self.host, self.headers, endpoint)
        rc = requests.post("%s/%s" % (self.host, endpoint),
                           json=data, headers=self.headers)
        if g_debug:
            print(rc.request.url)
            print(rc.json())
        if rc.status_code != 200:
            print("*** REST api error: %s" % rc.status_code)
        return rc.json(), 0 if rc.status_code == 200 else rc.status_code

    def get_alerts(self, count=None, ago=None, token=None, closed_alerts=False, all_alerts=False, tenant=None):
        """Fetches alerts
            Usage: alerts, next_page, status = api.get_alerts()
        """
        data = {
                "filter.openAlerts": True,
                "filter.closedAlerts": closed_alerts,
                "filter.listAllAlerts": all_alerts,
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
        return ret.get("insights", []), status

    def get_enforced(self, tenant=None):
        """Fetches enforced lenses
            Usage: lenses, status = api.get_enforced()
        """
        data = {}
        if tenant is None:
            if utils.cfg["tenant"]:
                data["tenant.id"] = utils.cfg["tenant"]
        else:
            data["tenant.id"] = tenant

        if g_debug: print(data)

        ret, status = self.get("api/v2/listShieldedLens", data)
        return ret.get("shielded_lens", []), status

    def set_enforced(self, op, zone=None, app=None, pod=None, container=None,
            process=None, parent=None, binpath=None, svc=None, svc_port=None, tenant=None):
        """Change the enforcement state of a lens
            Usage: status = api.set_enforced("DEL")
        """
        data = {"op": 2 if op=="DEL" else 1}
        if tenant is None:
            if utils.cfg["tenant"]:
                data["tenant"] = {"id": utils.cfg["tenant"]}
            else:
                assert False, "*** tenant not specified"
        else:
            data["tenant"] = {"id": tenant}

        if zone: data["zone"] = zone
        if app: data["app"] = app
        if svc:
            assert svc_port is not None, "both service and port need to be specified"
            data["service"] = svc
            data["service_port"] = int(svc_port)
        if container:
            assert None not in [zone, app, pod], "zone, app, and pod must be specified for the container"
            data["pod"] = pod
            data["container"] = container
        if process:
            assert None not in [zone, app, process, parent, binpath], "zone, app, process, parent, binpath must be specified"
            data["process"] = process
            data["parentProcess"] = parent
            data["binaryName"] = binpath

        if g_debug: print(data)

        ret, status = self.post("api/v2/setShieldStatus", data)
        return ret, status

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
            return ret.get("knobs", [])
        return None

    def update_fw_config(self, zone, tenant=None, data_file_location=None):
        """Update firewall knobs for a tenant in the zone
            Usage: status = api.update_fw_config()
        """
        if data_file_location:
            json_file_location = data_file_location
        else:
            json_file_location = "/tmp/fw_cfg.json"

        try:
            with open(json_file_location) as f:
                file_data = yaml.load(f, yaml.SafeLoader)
        except Exception as ex:
            print(ex)
            return "exception parsing json"

        if g_debug:
            print(file_data)

        data = {"knobs": file_data, "zone": zone}
        if tenant is None:
            if utils.cfg["tenant"]:
                data["tenant_id"] = utils.cfg["tenant"]
            else:
                assert False, "*** tenant not specified"
        else:
            data["tenant_id"] = tenant

        if g_debug:
            print(data)

        ret, status = self.post("api/v2/updateFirewallConfig", data)
        return status

    def get_helm_values(self, workload_name, nanny=None, tenant=None):
        """Fetches helm values for nanny/controller or firewall chart
            Usage: values_yaml = api.get_helm_values()
        """
        data = {"workload_name": workload_name}
        if tenant is None:
            if utils.cfg["tenant"]:
                data["tenant.id"] = utils.cfg["tenant"]
            else:
                assert False, "*** tenant not specified"
        else:
            data["tenant.id"] = tenant

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

    def delete_tenant(self, tenant=None):
        """Get pod name mapping for a zone
            Usage: values_yaml = api.get_pod_mapping()
        """
        if tenant is None:
            if utils.cfg["tenant"]:
                tenant = utils.cfg["tenant"]
            else:
                assert False, "*** tenant not specified"
        else:
            tenant = tenant

        data = {
            "tenant": {
              "id": tenant,
            }
        }

        if g_debug:
            print(data)

        ret, status = self.post("api/v2/deleteTenant", data)
        return ret, status

    def get_pod_mapping(self, zone, tenant=None):
        """Get pod name mapping for a zone
            Usage: values_yaml = api.get_pod_mapping()
        """
        data = {}
        if zone: data["zone"] = zone
        if tenant is None:
            if utils.cfg["tenant"]:
                data["tenant.id"] = utils.cfg["tenant"]
            else:
                assert False, "*** tenant not specified"
        else:
            data["tenant.id"] = tenant

        if g_debug:
            print(data)

        ret, status = self.get("api/v2/listPodNameMappings", data)
        return ret.get("pod_name_mapping", []), status

    def add_pod_mapping(self, zone, app, pattern, name, tenant=None):
        """Get pod name mapping for a zone
            Usage: values_yaml = api.get_pod_mapping()
        """
        if tenant is None:
            if utils.cfg["tenant"]:
                tenant = utils.cfg["tenant"]
            else:
                assert False, "*** tenant not specified"
        else:
            tenant = tenant

        data = {
                    "tenant": {
                        "id": tenant,
                    },
                    "pod_name_mapping": [
                        {
                            "zone": zone,
                            "app": app,
                            "pod_name_regex_pattern": pattern,
                            "translated_pod_name": name
                        }
                    ]
                }

        if g_debug:
            print(data)

        ret, status = self.post("api/v2/addPodNameMappings", data)
        return ret, status

    def del_pod_mapping(self, zone, app, pattern, name, tenant=None):
        """ Delete pod name mapping entry
            Usage: values_yaml = api.get_pod_mapping()
        """
        if tenant is None:
            if utils.cfg["tenant"]:
                tenant = utils.cfg["tenant"]
            else:
                assert False, "*** tenant not specified"
        else:
            tenant = tenant

        data = {
                    "tenant": {
                        "id": tenant,
                    },
                    "pod_name_mapping": [
                        {
                            "zone": zone,
                            "app": app,
                            "pod_name_regex_pattern": pattern,
                            "translated_pod_name": name
                        }
                    ]
                }

        if g_debug:
            print(data)

        ret, status = self.post("api/v2/deletePodNameMappings", data)
        return ret, status
