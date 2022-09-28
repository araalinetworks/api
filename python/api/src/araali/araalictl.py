"""fake api using araalictl underneath
    api = api.API()

    alerts, page, status = api.get_alerts(args.count, args.ago)
    assets, status = api.get_assets(args.zone, args.app, args.ago)
    links, status = api.get_links(args.zone, args.app, args.svc, args.ago)
    insights, status = api.get_insights(args.zone)
"""
from __future__ import print_function

from . import api
import datetime
import os
import platform
import requests
import subprocess
import sys
from . import utils
import yaml

g_debug = False
g_use_api = False

class API:
    def __init__(self):
        if g_use_api:
            self.api = api.API()
            return

        def fetch():
            """For downloading and upgrading araalictl"""
            progdir = os.path.dirname(os.path.abspath(__file__))
            afile = progdir + "/bin/araalictl"
            rc = utils.run_command("mkdir -p %s/bin" % (progdir), debug=g_debug, result=True, strip=False)
            afile = progdir + "/bin/araalictl"
            if os.path.isfile(afile):
                #print("upgrading araalictl ...")
                #rc = utils.run_command("sudo %s upgrade" % (afile), debug=g_debug, result=True, strip=False)
                return afile

            url = {
                    "Linux": "https://s3-us-west-2.amazonaws.com/araalinetworks.cf/araalictl-api.linux-amd64",
                    "Darwin": "https://s3-us-west-2.amazonaws.com/araalinetworks.cf/araalictl-api.darwin-amd64"
                  }.get(platform.system(), None)
            if url is None:
                raise Exception("*** only linux and mac are currently supported: %s" % platform)

            print("Fetching araalictl ...")
            r = requests.get(url, allow_redirects=True)
            open(afile, 'wb').write(r.content)
            os.chmod(afile, 0o777)
            return afile

        self.cmdline = fetch()

    def check(self):
        # nightly.aws.araalinetworks.com
        rc = utils.run_command("%s config InternalCfgBackend" % (self.cmdline),
                                debug=g_debug, result=True, strip=False)
        try:
            backend = rc[1].decode().split("=", 1)[1].split(".")[0]
        except:
            backend = None

        if backend != utils.cfg["backend"]:
            print("*** backend doesnt match, invoking deauth ...")
            os.system(("sudo %s authorize -clean" % (self.cmdline)))

        rc = utils.run_command("%s authorize check" % (self.cmdline),
                                debug=g_debug, result=True, strip=False)
        ret = rc[1].decode().strip()
        if ret != "copy is authorized":
            print("*** not authorized for %s, must re-authorize in Araali UI" % utils.cfg["backend"])
            rc = utils.run_command("sudo %s authorize -clean" % (self.cmdline),
                                debug=g_debug, result=True, strip=False)
            rc = utils.run_command("sudo rm -rf /tmp/actl* /tmp/av.port",
                                debug=g_debug, result=True, strip=False)
            cmdline = "sudo %s authorize -bend %s" % (self.cmdline, utils.cfg["backend"])
            #cmdline = "sudo %s authorize -local" % (self.cmdline)
            os.system(cmdline)

        if "email" not in utils.cfg:
            # DevName=blah@blah.com
            rc = utils.run_command("%s config DevName" % (self.cmdline),
                                debug=g_debug, result=True, strip=False)
            utils.cfg["email"] = rc[1].decode().split("=", 1)[1]

    def get_tenants(self):
        self.check()

        rc = utils.run_command("%s api -fetch-active-subtenants" % (
                                self.cmdline),
                                debug=g_debug, result=True, strip=False)

        if rc[0] != 0:
            print("*** failed: %s" % rc[1].decode())
        return yaml.load(rc[1], yaml.SafeLoader), rc[0]

    def get_alerts(self, count=None, ago=None, token=None, tenant=None):
        """get alerts"""

        if g_use_api:
            return self.api.get_alerts(count, ago, token, tenant)

        self.check()
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

        if rc[0] != 0:
            print("*** failed: %s" % rc[1].decode())
        token = None
        objs = yaml.load(rc[1], yaml.SafeLoader)
        if objs:
            token=objs[-1].get("paging_token", None)

        return objs, token, rc[0]

    def get_assets(self, zone=None, app=None, ago=None, tenant=None):
        """Get assets for a zone (required) and app (optional)
            Usage: assets, status = api.get_assets()
        """

        if g_use_api:
            return self.api.get_assets(zone, app, ago, tenant)

        self.check()
        if not ago:
            ago = "days=1"
        ago = dict([utils.make_map(a) for a in ago.split(",")])
        start_time = datetime.datetime.now() - datetime.timedelta(**ago)
        end_time = datetime.datetime.now()

        cmd = "-starttime %s" % (int(start_time.timestamp()))
        cmd += " -endtime %s" % (int(end_time.timestamp()))
        if zone: cmd += " -zone %s" % zone
        if app: cmd += " -app %s" % app
        if tenant is None: tenant = utils.cfg["tenant"]
        if tenant: cmd += " -tenant %s" % tenant

        rc = utils.run_command("%s api %s -fetch-compute" % (
            self.cmdline, cmd), debug=g_debug, result=True, strip=False)
        if rc[0] != 0:
            print("*** failed: %s" % rc[1].decode())
        return yaml.load(rc[1], yaml.SafeLoader), rc[0]

    def get_links(self, zone=None, app=None, svc=None, ago=None, tenant=None):
        """Get links for a zone and app, or svc"""

        if g_use_api:
            return self.api.get_links(zone, app, svc, ago, tenant)
        self.check()
        assert svc is not None or zone is not None and app is not None

        if tenant is None: tenant = utils.cfg["tenant"]
        tstr = " -tenant=%s " % (tenant) if tenant else ""
        if svc:
            tstr += " -service=%s " % (svc)
        else:
            tstr += " -zone=%s -app=%s " % (zone, app)

        if not ago:
            ago = "days=1"
        ago = dict([utils.make_map(a) for a in ago.split(",")])
        start_time = datetime.datetime.now() - datetime.timedelta(**ago)
        end_time = datetime.datetime.now()
        tstr += " -starttime %s" % (int(start_time.timestamp()))
        tstr += " -endtime %s" % (int(end_time.timestamp()))

        rc = utils.run_command("%s api -fetch-links %s" % (self.cmdline, tstr),
                         debug=g_debug, result=True, strip=False)
        if rc[0] != 0:
            print("*** failed: %s" % rc[1].decode())
        return yaml.load(rc[1], yaml.SafeLoader), rc[0]

    def get_insights(self, zone=None, tenant=None):
        """Get insights for a zone (optional)"""

        if g_use_api:
            return self.api.get_insights(zone, tenant)
        self.check()
        cmd = ""
        if zone: cmd += " -zone %s" % zone
        if tenant is None: tenant = utils.cfg["tenant"]
        if tenant: cmd += " -tenant %s" % tenant

        rc = utils.run_command("%s api %s -fetch-insights" % (
            self.cmdline, cmd), debug=g_debug, result=True, strip=False)
        if rc[0] != 0:
            print("*** failed: %s" % rc[1].decode())
        return yaml.load(rc[1], yaml.SafeLoader), rc[0]

    def token(self, op=None, name=None, email=None, tenant=None):
        """token management"""

        self.check()
        if op == None:
            print("*** operation not specified")
            return
        if email is None: email = utils.cfg["email"]
        if op == "add":
            cmd = "-name=%s %s" % (name, email)
        elif op == "delete":
            cmd = "-delete -name=%s %s" % (name, email)
        else:
            cmd = "-list"

        #if tenant is None: tenant = utils.cfg["tenant"]
        #if tenant: cmd += " -tenant=%s" % tenant

        rc = utils.run_command("%s token -api-access %s" % (
            self.cmdline, cmd), debug=g_debug, result=True, strip=False)
        if rc[0] != 0:
            print("*** failed: %s" % rc[1].decode())
        return yaml.load(rc[1], yaml.SafeLoader), rc[0]

    def get_templates(self, public=None, template=None, tenant=None):
        """Get templates (or public ones)"""

        self.check()

        if tenant is None: tenant = utils.cfg["tenant"]
        tstr = " -tenant=%s " % (tenant) if tenant else ""
        tstr += " -public " if public else ""
        tstr += " -template=%s " % (template) if template else ""

        rc = utils.run_command("%s api -list-templates %s" % (
            self.cmdline, tstr), debug=g_debug, result=True, strip=False)
        if rc[0] != 0:
            print("*** failed: %s" % rc[1].decode())
        return yaml.load(rc[1], yaml.SafeLoader), rc[0]

    def update_template(self, data, public=False, tenant=None):
        """Update template"""

        self.check()

        if tenant is None: tenant = utils.cfg["tenant"]
        tstr = " -tenant=%s " % (tenant) if tenant else ""

        command = "-update-template" if not public else "-export-template"
        rc = utils.run_command("%s api %s %s" % (
            self.cmdline, command, tstr), in_text=yaml.dump(data), debug=g_debug, result=True, strip=False)
        if rc[0] != 0:
            print("*** failed: %s" % rc[1].decode())
        return yaml.load(rc[1], yaml.SafeLoader), rc[0]

    def get_zones_apps(self, full=False, tenant=None):
        """Get zones and apps"""
        self.check()

        if tenant is None: tenant = utils.cfg["tenant"]
        tstr = " -tenant=%s " % (tenant) if tenant else ""
        rc = utils.run_command("%s api -fetch-zone-apps %s %s" % (self.cmdline, "-full" if full else "", tstr),
                result=True, debug=g_debug, strip=False)
        if rc[0] != 0:
            print("*** failed: %s" % rc[1].decode())
        return yaml.load(rc[1], yaml.SafeLoader), rc[0]

    def get_helm_values(self, zone=None, tenant=None):
        """Get helm chart"""
        self.check()

        if tenant is None: tenant = utils.cfg["tenant"]
        tstr = " -tenant=%s " % (tenant) if tenant else ""
        if zone is not None:
            tstr += " -tags=zone=%s " % zone
        rc = utils.run_command("%s fortify-k8s -out helm %s" % (self.cmdline, tstr),
                result=True, debug=g_debug, strip=False)
        if rc[0] != 0:
            print("*** failed: %s" % rc[1].decode())
        return yaml.load(rc[1], yaml.SafeLoader), rc[0]

    def rbac_show_users(self, tenant=None):
        """show rbac"""

        self.check()
                                                     
        tstr = " -tenant=%s " % (tenant) if tenant else ""
        rc = utils.run_command("%s user-role -op list-user-roles %s" % (
                         self.cmdline, tstr), result=True, debug=g_debug, strip=False)
        if rc[0] != 0:
            print("*** failed: %s" % rc[1].decode())
        return yaml.load(rc[1], yaml.SafeLoader), rc[0]

