"""Used to execute modeule from the command line
    Fetches alerts and prints the count
"""
import argparse
import datetime
from dateutil import parser as du_parser
from dateutil import tz
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import yaml

from araali import API
from . import api
from . import araalictl
from . import utils
from . import template as module_template

def config(args):
    if args.get_tenants:
        """
        Current:
            ./araalictl api -fetch-active-subtenants
            ./araalictl api -fetch-subtenants
            ./araalictl api -tenant=freemium -fetch-subtenants

        Desired:
            ./araalictl api -fetch-subtenants
            ./araalictl api -fetch-subtenants -active
        """
        if utils.cfg["backend"] != "prod": utils.config(backend="prod")
        tracking = [a["id"] for a in utils.cfg.get("tenants", [])]
        obj = araalictl.API().get_tenants()[0]["subtenantlist"]
        # ['tenantid', 'adminemail', 'activevmcount', 'activecontainercount', 'perimeteralertcount', 'homealertcount', 'lastsignedin']
        print("     %-22s %-42s %-7s %-10s %s" % ("tenant-id", "admin-email", "count", "tracked", "last-signed-in"))
        agent_count = 0
        for i, o in enumerate(obj):
            o["lastsignedin"] = datetime.datetime.fromtimestamp(o["lastsignedin"]/1000) if o["lastsignedin"] else ""
            print("%3s: t=%-20s e=%-40s c=%-5s tr=%-7s s=%s" % (i+1, o["tenantid"],
                o["adminemail"], o["activevmcount"], o["tenantid"] in tracking,
                o["lastsignedin"] if o["lastsignedin"] else "nil"))
            agent_count += o["activevmcount"]
        print("Total agents: %s" % agent_count)
        return
    return utils.config(args.tenant, args.tenants, args.template_dir, args.backend)

def alerts(args):
    alerts, page, status = API().get_alerts(args.count, args.ago, tenant=args.tenant)
    day_dict = {}
    local_zone = tz.tzlocal()
    if status == 0:
        print("Got %s alerts" % len(alerts))
        utils.dump_table(alerts)

        for a in alerts:
            if type(a["timestamp"]) == str:
                # '2022-07-15T04:45:18Z'
                dt = du_parser.parse(a["timestamp"]).astimezone(local_zone)
            else:
                dt = datetime.datetime.fromtimestamp(a["timestamp"]/1000)
            #dts = dt.strftime("%m/%d/%Y, %H:%M:%S")
            dts = dt.strftime("%Y/%m/%d")
            day_dict.setdefault(dts, []).append(a)

        keys = [a for a in day_dict.keys()]
        keys.sort()
        print("frequency count")
        for k in keys:
            print("%s %s" % (k, len(day_dict[k])))

def make_map(kv):
    k, v = kv.split("=")
    return k, v

def assets(args):
    if not args.nopull or not os.path.isfile("%s/%s/dump.json" % (args.progdir, ".assets.araali")):
        shutil.rmtree("%s/%s" % (args.progdir, ".assets.araali"), ignore_errors=True)
        os.makedirs("%s/%s" % (args.progdir, ".assets.araali"), exist_ok=True)
        with open("%s/%s/dump.json" % (args.progdir, ".assets.araali"), "w") as f:
            assets, status = API().get_assets(args.zone, args.app, args.ago, tenant=args.tenant)
            if status == 0:
                for a in assets:
                    json.dump(a, f)
                    f.write("\n")

                #print("Got %s assets" % len(assets))
                #utils.dump_table(assets)

    if args.filters:
        filters = dict([make_map(a) for a in args.filters.split(",")])
    else:
        filters = {}

    i = 0
    search_type = "asset"
    if set(["cve", "cve_sev"]) & set(filters):
        search_type = "cve"

    def cve_in_asset(line, filters):
        for v in line["vulnerabilities"]:
            for c in v["cve_id"]:
                if re.search(filters["cve"], c):
                    return True
        return False

    def match_filters(filters, line):
        def get_app_name(a):
            if type(a) == dict:
                return a["app_name"]
            return a

        for k,v in filters.items():
            if k == "app":
                if not re.search(":[^:]*" + v + "[^:]*:", ":"+ ":".join([get_app_name(a) for a in line["apps"]]) + ":"):
                    return False
            elif k not in line:
                return False
            else:
                if not re.search(v, line[k]):
                    return False
        return True

    cve_sev_map = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    with open("%s/%s/dump.json" % (args.progdir, ".assets.araali"), "r") as f:
        for line in f:
            line = json.loads(line)
            # 'name', 'ip_address', 'uuid', 'image', 'zone', 'apps', 'processes', 'state', 'asset_type', 'process_capabilities', 'ip_addresses', 'originaluuid', 'vulnerabilities', 'mode', 'os_name'
            if args.verbose > 1:
                print("="*40, i, "="*40)
                print("name", line["name"])
                print("ip", line["ip_address"])
                print("uuid", line["uuid"])
                print("orig_uuid", line["originaluuid"])
                print("image", line["image"])
                print("zone", line.get("zone", ""))
                print("apps", line.get("app", ""))
                #print("process", line.get("process", "")) # always empty
                print("state", line["state"])
                print("asset_type", line["asset_type"])
                #print("process_capabilities", line["process_capabilities"]) # always empty
                print("mode", line["mode"])
                print("os_name", line["os_name"])
                #print("ip_addresses", line["ip_addresses"]) # always empty
                # 'package_name', 'cve_id', 'severity'
                #print("cve", line["vulnerabilities"][0].keys()) # always empty

            line["cve_count"] = str(len(line.get("vulnerabilities", [])))
            if search_type == "cve":
                if "vulnerabilities" not in line or not line["vulnerabilities"]:
                    continue

                if "cve" in filters and cve_in_asset(line, filters):
                    print("="*40, i, "="*40)
                    i += 1
                    line["max_severity"] = max([cve_sev_map[a["severity"]] for a in line["vulnerabilities"]])
                    if not args.verbose:
                        del line["vulnerabilities"]
                    if "containerd" in line:
                        line["caps"] = len(line["containerd"]["capabilities"])
                        del line["containerd"]["capabilities"]
                    print(yaml.dump(line))
                elif "cve_sev" in filters and max([cve_sev_map[a["severity"]] for a in line["vulnerabilities"]]) == int(filters["cve_sev"]):
                    print("="*40, i, "="*40)
                    i += 1
                    line["max_severity"] = max([cve_sev_map[a["severity"]] for a in line["vulnerabilities"]])
                    del line["vulnerabilities"]
                    if "containerd" in line:
                        line["caps"] = len(line["containerd"]["capabilities"])
                        del line["containerd"]["capabilities"]
                    print(yaml.dump(line))

            else:
                if match_filters(filters, line):
                    print("="*40, i, "="*40)
                    i += 1
                    if "vulnerabilities" in line:
                        del line["vulnerabilities"]
                    if "containerd" in line:
                        line["caps"] = len(line["containerd"]["capabilities"])
                        #del line["containerd"]["capabilities"]
                    print(yaml.dump(line))


def links(args):
    links, status = API().get_links(args.zone, args.app, args.svc, args.ago, tenant=args.tenant)
    if status == 0:
        print("Got %s links" % len(links))
        utils.dump_table(links)

def search(args):
    def match_filters(filters, line):
        for k,v in filters.items():
            if k not in line:
                if args.verbose: print("***", k, "not in", line)
                return False
            else:
                if not re.search(v, line[k]):
                    if args.verbose: print("***", v, "doesnt match", line[k])
                    return False
        return True

    if not args.nopull or not os.path.isfile("%s/%s/dump.json" % (args.progdir, ".za.araali")):
        shutil.rmtree("%s/%s" % (args.progdir, ".za.araali"), ignore_errors=True)
        os.makedirs("%s/%s" % (args.progdir, ".za.araali"), exist_ok=True)
        with open("%s/%s/dump.json" % (args.progdir, ".za.araali"), "w") as f:
            zones_apps, status = API().get_zones_apps(full=True, tenant=args.tenant)
            if status == 0:
                # [{"zone_name": xx, "apps": [{"app_name": xx, "links": []}]}]
                for za in zones_apps:
                    json.dump(za, f)
                    f.write("\n")

    # Three types of searches: asset, workload, service, link (in future file and fork)
    if args.filters:
        filters = dict([make_map(a) for a in args.filters.split(",")])
    else:
        filters = {}
    for k in ["zone", "app", "pod", "container"]:
        if k not in filters:
            filters[k] = ".*"

    search_type = "asset" # container, app/VM
    filter_keys = set(filters.keys())
    if set(["process", "binary_name", "parent_process"]) & filter_keys:
        search_type = "workload" # process lens
        for k in ["process", "binary_name", "parent_process"]:
            if k not in filters:
                filters[k] = ".*"
    elif set(["dns_pattern", "dst_port"]) & filter_keys:
        search_type = "service" # service lens
        for k in ["dns_pattern", "dst_port"]:
            if k not in filters:
                filters[k] = ".*"

    if args.verbose: print("filter:", filters)
    if args.verbose: print("search_type:", search_type)
    i = 0
    workload_dict = {}
    with open("%s/%s/dump.json" % (args.progdir, ".za.araali"), "r") as f:
        for line in f:
            zapps = json.loads(line)
            zname, apps = zapps["zone_name"], zapps["apps"]
            if not re.search(filters["zone"], zname):
                continue
            for app in apps:
                aname, links = app["app_name"], app.get("links", [])
                if not re.search(filters["app"], aname):
                    continue

                if search_type == "asset":
                    wkey = ":".join([zname, aname])
                    if wkey not in workload_dict:
                        print("="*40, i, "="*40)
                        i += 1
                        print(yaml.dump({"zone": zname, "app": aname}))
                        workload_dict[wkey] = 1
                    else:
                        workload_dict[wkey] += 1
                        raise # not expected to come here
                    continue

                for link in links:
                    # ['client', 'server', 'type', 'policy_skip_reason', 'error_code',
                    #  'state', 'timestamp', 'unique_id', 'alert_info', 'rollup_ids', 'active_ports']
                    client = link["client"]
                    server = link["server"]
                    # ['zone', 'app', 'unmapped_app', 'process', 'binary_name', 'parent_process']
                    if search_type == "workload":
                        nfilters = dict([a for a in filters.items() if a[0] not in ["zone", "app", "pod", "container"]])
                        client_m = match_filters(nfilters, client)
                        # {'subnet': '0.0.0.0', 'private_subnet': True} HOME
                        server_m = match_filters(nfilters, server)
                        # {'dns_pattern': '.*:dynamodb.*amazonaws.com:.*', 'dst_port': 443}

                        if search_type == "link":
                            if client_m or server_m:
                                print("="*40, i, "="*40)
                                i += 1
                                print(yaml.dump({"client": client, "server": server}))
                        else:
                            if client_m:
                                wkey = [str(a) for a in client.values()]
                                wkey.sort()
                                wkey = ":".join(wkey)
                                if wkey not in workload_dict:
                                    print("="*40, i, "="*40)
                                    i += 1
                                    print(yaml.dump(client))
                                    workload_dict[wkey] = 1
                                else:
                                    workload_dict[wkey] += 1

                            if server_m:
                                wkey = [str(a) for a in server.values()]
                                wkey.sort()
                                wkey = ":".join(wkey)
                                if wkey not in workload_dict:
                                    print("="*40, i, "="*40)
                                    i += 1
                                    print(yaml.dump(server))
                                    workload_dict[wkey] = 1
                                else:
                                    workload_dict[wkey] += 1
                    elif search_type == "service" and "dst_port" in server:
                        if "dns_pattern" in server:
                            dns_m = re.search(filters["dns_pattern"], server["dns_pattern"])
                            wkey = ":".join([server["dns_pattern"], str(server["dst_port"])])
                        elif "subnet" in server:
                            # {'subnet': '169.254.169.254', 'netmask': 32, 'dst_port': 80}
                            dns_m = re.search(filters["dns_pattern"], server["subnet"])
                            wkey = ":".join([server["subnet"], str(server["dst_port"])])
                        else:
                            dns_m = None
                            assert(server)
                        port_m = re.search(filters["dst_port"], str(server["dst_port"]))
                        if dns_m and port_m:
                            if wkey not in workload_dict:
                                print("="*40, i, "="*40)
                                i += 1
                                print(yaml.dump(server))
                                workload_dict[wkey] = 1
                            else:
                                workload_dict[wkey] += 1
        if 1:
            keys = list(workload_dict.keys())
            keys.sort(key=lambda x: -workload_dict[x])
            print("Found %s items" % len(keys))
            count = 0
            for i, k in enumerate(keys):
                print("%3s: %05s %s" % (i, workload_dict[k], k))
                count += workload_dict[k]
            print("Total count: %s" % count)

def helm(args):
    print(yaml.dump(araalictl.API().get_helm_values(args.zone, args.tenant)[0]))

def insights(args):
    insights, status = API().get_insights(args.zone, tenant=args.tenant)
    if status == 0:
        utils.dump_table(insights)

def token(args):
    if args.add:
        op = "add"
        name = args.add
    elif args.delete:
        op = "delete"
        name = args.delete
    elif args.list:
        op = "show"
        name = None
    tokens, status = araalictl.API().token(op=op, name=name, email=args.email, tenant=args.tenant)
    if status == 0:
        if op == "show":
            utils.dump_table(tokens["tokens"])
        else:
            print(tokens)

def ctl(args, remaining):
    api = araalictl.API()
    if remaining and remaining[0] not in ["authorize"]:
        api.check()

    if remaining and remaining[0] == "--": remaining = remaining[1:]

    if remaining and remaining[0] in ["authorize", "upgrade"]:
        prepend = ["sudo"]
    else:
        prepend = []

    #p = subprocess.Popen(["sudo", cmdline, "authorize", "-token=-"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
    #auth_stdout = p.communicate(input=api.cfg["token"].encode())[0]
    #print("echo %s | sudo %s authorize -token=-" % (api.cfg["token"], cmdline))
    #print(auth_stdout.decode())

    rc = subprocess.run(prepend + [api.cmdline] + remaining)
    return rc.returncode

def template(args):
    if args.t_subparser_name:
        return getattr(module_template, args.t_subparser_name)(args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Araali Python CLI')
    parser.add_argument('--verbose', '-v', action='count', default=0, help="specify multiple times to increase verbosity (-vvv)")
    parser.add_argument('--use_api', '-u', action='store_true', help="user api instead of araalictl")
    subparsers = parser.add_subparsers(dest="subparser_name")

    parser_config = subparsers.add_parser("config", help="list/change config params")
    parser_config.add_argument('-t', '--tenant', help="setup sub-tenant param (sticky)")
    parser_config.add_argument('--tenants', help="setup a list of sub-tenants (for managing alerts)")
    parser_config.add_argument('--backend', help="setup a custom backend (internal unit testing)")
    parser_config.add_argument('-g', '--get_tenants', action="store_true", help="get active tenants")
    parser_config.add_argument('-d', '--template_dir', help="custom template directory")

    parser_alerts = subparsers.add_parser("alerts", help="get alerts (to create templates for)")
    parser_alerts.add_argument('-t', '--tenant', help="get alert for a specific tenant")
    parser_alerts.add_argument('-n', '--nopull', action="store_true", help="dont pull from araali")
    parser_alerts.add_argument('-c', '--count', type=int, help="dont pull from araali")
    parser_alerts.add_argument('--ago', help="lookback")

    parser_insights = subparsers.add_parser("insights", help="get insights")
    parser_insights.add_argument('-t', '--tenant', help="get insights for a specific tenant")
    parser_insights.add_argument('-z', '--zone', help="insights for a specific zone")

    parser_assets = subparsers.add_parser("assets", help="get assets")
    parser_assets.add_argument('-t', '--tenant', help="get assets for a specific tenant")
    parser_assets.add_argument('-z', '--zone', help="assets for a specific zone")
    parser_assets.add_argument('-a', '--app', help="links for a specific app")
    parser_assets.add_argument('-n', '--nopull', action="store_true", help="dont pull from araali")
    parser_assets.add_argument('-f', '--filters', help="query filters. eg: zone=.*,app=.*,cve_sev=4,cve_count=^0$")
    parser_assets.add_argument('--ago', help="lookback")

    parser_token = subparsers.add_parser("token", help="manage api tokens")
    parser_token.add_argument('-t', '--tenant', help="token management for a specific tenant")
    parser_token.add_argument('-a', '--add', help="create new token")
    parser_token.add_argument('-d', '--delete', help="delete token by name")
    parser_token.add_argument('-e', '--email', help="user email")
    parser_token.add_argument('-l', '--list', action="store_true", help="list all tokens")

    parser_links = subparsers.add_parser("links", help="get links")
    parser_links.add_argument('-t', '--tenant', help="get links for a specific tenant")
    parser_links.add_argument('-z', '--zone', help="links for a specific zone")
    parser_links.add_argument('-a', '--app', help="links for a specific app")
    parser_links.add_argument('-s', '--svc', help="links for a specific svc")
    parser_links.add_argument('--ago', help="lookback")

    parser_za = subparsers.add_parser("search", help="search assets, workloads, services")
    parser_za.add_argument('-t', '--tenant', help="get zones and apps for a specific tenant")
    parser_za.add_argument('-n', '--nopull', action="store_true", help="dont pull from araali")
    parser_za.add_argument('-f', '--filters', help="query filters. eg: zone=.*,app=.*,pod=.*,container=.* process=.*,binary_name=.*,parent_process=.*,dns_pattern=.*,dst_port=.*")

    parser_helm = subparsers.add_parser("helm", help="generate values for araaly firewall helm chart")
    parser_helm.add_argument('-t', '--tenant', help="helm chart for a specific tenant")
    parser_helm.add_argument('-z', '--zone', help="helm for a specific zone")

    parser_ctl = subparsers.add_parser("ctl", help="run araalictl commands")

    parser_template = subparsers.add_parser("template", help='Manage Templates as Code (in Git)')
    parser.add_argument('-T', '--template', help="apply operation for a specific template")

    t_subparsers = parser_template.add_subparsers(dest="t_subparser_name")

    parser_alerts = t_subparsers.add_parser("alerts", help="get alerts (to create templates for)")
    parser_alerts.add_argument('-t', '--tenant', help="get alert for a specific tenant")
    parser_alerts.add_argument('-n', '--nopull', action="store_true", help="dont pull from araali")
    parser_alerts.add_argument('-a', '--ago', help="dont pull from araali")

    parser_drift = t_subparsers.add_parser("drift", help="get drift (from template as code)")
    parser_drift.add_argument('-t', '--tenant', help="get drift for a specific tenant")
    parser_drift.add_argument('-p', '--public', action="store_true", help="drift in public library")
    parser_drift.add_argument('-n', '--nopull', action="store_true", help="dont pull from araali")
    parser_drift.add_argument('-T', '--template', help="get drift for a specific template (name or path)")

    parser_list = t_subparsers.add_parser("ls", help="list templates")
    parser_list.add_argument('-p', '--public', action="store_true", help="list from public library")
    parser_list.add_argument('-t', '--tenant', help="list for a sub-tenant")
    parser_list.add_argument('-T', '--template', help="list a specific template (name or path)")

    parser_pull = t_subparsers.add_parser("pull", help="pull templates")
    parser_pull.add_argument('-p', '--public', action="store_true", help="pull from public library")
    parser_pull.add_argument('-T', '--template', help="pull a specific template (name or path)")
    parser_pull.add_argument('-t', '--tenant')

    parser_push = t_subparsers.add_parser("push", help="push templates")
    parser_push.add_argument('-p', '--public', action="store_true", help="push to public library")
    parser_push.add_argument('-T', '--template', help="push a specific template (name or path)")
    parser_push.add_argument('-t', '--tenant', help="push for a sub-tenant")

    parser_format = t_subparsers.add_parser("fmt", help="rename template node name/ format into a normalized form")
    parser_format.add_argument('template')

    args, remaining = parser.parse_known_args()
    args.progdir, args.prog = os.path.split(sys.argv[0])

    if args.verbose:
        api.g_debug = True
        araalictl.g_debug = True

    if args.use_api:
        araalictl.g_use_api = True

    if args.subparser_name == "ctl":
        sys.exit(ctl(args, remaining))
    elif remaining:
        raise Exception("*** unknown flags: %s" % remaining)

    if args.template: # template can be specified by name or file path
        args.dirname, args.pathname = os.path.split(args.template)
        args.template = args.pathname.split(".yaml")[0]

    if args.subparser_name:
        sys.exit(locals()[args.subparser_name](args))
    else:
        araalictl.API().check()

    sys.exit(0)
