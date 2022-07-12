"""Used to execute modeule from the command line
    Fetches alerts and prints the count
"""
import argparse
import os
import platform
import subprocess
import sys

from . import api

def config(args):
    return api.config(args.tenant, args.tenants, args.template_dir, args.backend, args.token)

def alerts(args):
    alerts, page, status = api.API().get_alerts(args.ago)
    if status == 0:
        api.dump_table(alerts)

def assets(args):
    assets, status = api.API().get_assets(args.zone, args.app, args.ago)
    if status == 0:
        api.dump_table(assets)

def links(args):
    links, status = api.API().get_links(args.zone, args.app, args.svc, args.ago)
    if status == 0:
        api.dump_table(links)

def insights(args):
    insights, status = api.API().get_insights(args.zone)
    if status == 0:
        api.dump_table(insights)

def ctl(args, remaining):
    cmdline = {
                "Linux": "araalictl.linux-amd64",
                "Darwin": "araalictl.darwin-amd64"
              }[platform.system()]
    cmdline = args.progdir + "/bin/" + cmdline

    if remaining[0] == "--": remaining = remaining[1:]

    if remaining and remaining[0] in ["authorize", "upgrade"]:
        prepend = ["sudo"]
    else:
        prepend = []

    #p = subprocess.Popen(["sudo", cmdline, "authorize", "-token=-"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
    #auth_stdout = p.communicate(input=api.cfg["token"].encode())[0]
    #print("echo %s | sudo %s authorize -token=-" % (api.cfg["token"], cmdline))
    #print(auth_stdout.decode())

    rc = subprocess.run(prepend + [cmdline] + remaining)
    return rc.returncode

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Araali Python CLI')
    parser.add_argument('--verbose', '-v', action='count', default=0, help="specify multiple times to increase verbosity (-vvv)")
    parser.add_argument('-T', '--template', help="apply operation for a specific template")
    subparsers = parser.add_subparsers(dest="subparser_name")

    parser_config = subparsers.add_parser("config", help="list/change config params")
    parser_config.add_argument('-t', '--tenant', help="setup sub-tenant param (sticky)")
    parser_config.add_argument('--tenants', help="setup a list of sub-tenants (for managing alerts)")
    parser_config.add_argument('--backend', help="setup a custom backend (internal unit testing)")
    parser_config.add_argument('--token', help="api access token")
    parser_config.add_argument('-d', '--template_dir', help="custom template directory")

    parser_alerts = subparsers.add_parser("alerts", help="get alerts (to create templates for)")
    parser_alerts.add_argument('-t', '--tenant', help="get alert for a specific tenant")
    parser_alerts.add_argument('-n', '--nopull', action="store_true", help="dont pull from araali")
    parser_alerts.add_argument('--ago', help="lookback")

    parser_insights = subparsers.add_parser("insights", help="get insights")
    parser_insights.add_argument('-t', '--tenant', help="get insights for a specific tenant")
    parser_insights.add_argument('-z', '--zone', help="insights for a specific zone")

    parser_assets = subparsers.add_parser("assets", help="get assets")
    parser_assets.add_argument('-t', '--tenant', help="get assets for a specific tenant")
    parser_assets.add_argument('-z', '--zone', help="assets for a specific zone")
    parser_assets.add_argument('-a', '--app', help="links for a specific app")
    parser_assets.add_argument('--ago', help="lookback")

    parser_links = subparsers.add_parser("links", help="get links")
    parser_links.add_argument('-t', '--tenant', help="get links for a specific tenant")
    parser_links.add_argument('-z', '--zone', help="links for a specific zone")
    parser_links.add_argument('-a', '--app', help="links for a specific app")
    parser_links.add_argument('-s', '--svc', help="links for a specific svc")
    parser_links.add_argument('--ago', help="lookback")

    parser_ctl = subparsers.add_parser("ctl", help="run araalictl commands")

    args, remaining = parser.parse_known_args()
    args.progdir, args.prog = os.path.split(sys.argv[0])

    if args.subparser_name == "ctl":
        sys.exit(ctl(args, remaining))
    elif remaining:
        raise Exception("*** unknown flags: %s" % remaining)

    if args.template: # template can be specified by name or file path
        args.dirname, args.pathname = os.path.split(args.template)
        args.template = args.pathname.split(".yaml")[0]

    if args.subparser_name:
        sys.exit(locals()[args.subparser_name](args))

    sys.exit(0)
