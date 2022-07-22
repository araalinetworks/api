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
        tracking = [a["id"] for a in utils.cfg["tenants"]]
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

def assets(args):
    assets, status = API().get_assets(args.zone, args.app, args.ago, tenant=args.tenant)
    if status == 0:
        print("Got %s assets" % len(assets))
        utils.dump_table(assets)

def links(args):
    links, status = API().get_links(args.zone, args.app, args.svc, args.ago, tenant=args.tenant)
    if status == 0:
        print("Got %s links" % len(links))
        utils.dump_table(links)

def za(args):
    if not args.nopull:
        shutil.rmtree("%s/%s" % (args.progdir, ".za.araali"), ignore_errors=True)
        os.makedirs("%s/%s" % (args.progdir, ".za.araali"), exist_ok=True)
        with open("%s/%s/dump.json" % (args.progdir, ".za.araali"), "w") as f:
            zones_apps, status = API().get_zones_apps(full=args.full, tenant=args.tenant)
            if status == 0:
                # [{"zone_name": xx, "apps": [{"app_name": xx, "links": []}]}]
                for za in zones_apps:
                    json.dump(za, f)
                    f.write("\n")
    else:
        def make_map(kv):
            k, v = kv.split("=")
            return k, v
        if args.filters:
            filters = dict([make_map(a) for a in args.filters.split(",")])
        else:
            filters = {}
        for k in ["zone", "app", "pod", "container", "process"]:
            if k not in filters:
                filters[k] = ".*"

        i = 0
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
                    for link in links:
                        # ['client', 'server', 'type', 'policy_skip_reason', 'error_code',
                        #  'state', 'timestamp', 'unique_id', 'alert_info', 'rollup_ids', 'active_ports']
                        client = link["client"]
                        server = link["server"]
                        # ['zone', 'app', 'unmapped_app', 'process', 'binary_name', 'parent_process']
                        if not re.search(filters["process"], client.get("process", "")) and not re.search(filters["process"], server.get("process", "")):
                            continue
                        print("="*40, i, "="*40)
                        i += 1
                        print(yaml.dump({"client": client, "server": server}))

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

    parser_za = subparsers.add_parser("za", help="get zones and apps")
    parser_za.add_argument('-t', '--tenant', help="get zones and apps for a specific tenant")
    parser_za.add_argument('-F', '--full', action="store_true", help="full dump")
    parser_za.add_argument('-n', '--nopull', action="store_true", help="dont pull from araali")
    parser_za.add_argument('-f', '--filters', help="query filters")

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
