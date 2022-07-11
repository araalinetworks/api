"""Used to execute modeule from the command line
    Fetches alerts and prints the count
"""
import argparse
import os
import sys
import yaml

from . import api

cfg_fname = os.environ['HOME']+"/.araalirc"

def read_config():
    if os.path.isfile(cfg_fname):
        with open(cfg_fname, "r") as f:
            cfg = yaml.load(f, Loader=yaml.SafeLoader)
            if not cfg.get("tenant", None): cfg["tenant"] = None
            if not cfg.get("template_dir", None): cfg["template_dir"] = "../templates"
            return cfg
    return {"tenant": None, "template_dir": "../templates"}

def config(args):
    global cfg
    if args.tenant is not None:
        if not args.tenant: # passed as empty string
            args.tenant = None # store it as nil in yaml
        cfg["tenant"] = args.tenant
        with open(cfg_fname, "w") as f:
            yaml.dump(cfg, f)
    if args.tenants is not None:
        cfg["tenants"] = [dict(zip(["name", "id"], a.split(":"))) for a in args.tenants.split(",")]
        with open(cfg_fname, "w") as f:
            yaml.dump(cfg, f)
    if args.template_dir is not None:
        cfg["template_dir"] = args.template_dir
        with open(cfg_fname, "w") as f:
            yaml.dump(cfg, f)
    print(yaml.dump(cfg))

def alerts(args):
    print(len(api.API().get_alerts()[0]), "alerts")

if __name__ == "__main__":
    cfg = read_config()
    parser = argparse.ArgumentParser(description = 'Araali Python CLI')
    parser.add_argument('--verbose', '-v', action='count', default=0, help="specify multiple times to increase verbosity (-vvv)")
    parser.add_argument('-T', '--template', help="apply operation for a specific template")
    subparsers = parser.add_subparsers(dest="subparser_name")

    parser_config = subparsers.add_parser("config", help="list/change config params")
    parser_config.add_argument('-t', '--tenant', help="setup sub-tenant param (sticky)")
    parser_config.add_argument('--tenants', help="setup a list of sub-tenants (for managing alerts)")
    parser_config.add_argument('-d', '--template_dir', help="custom template directory")

    parser_alerts = subparsers.add_parser("alerts", help="get alerts (to create templates for)")
    parser_alerts.add_argument('-t', '--tenant', help="get alert for a specific tenant")
    parser_alerts.add_argument('-n', '--nopull', action="store_true", help="dont pull from araali")
    parser_alerts.add_argument('-a', '--ago', help="dont pull from araali")

    args = parser.parse_args()
    args.progdir, args.prog = os.path.split(sys.argv[0])
    if args.template: # template can be specified by name or file path
        args.dirname, args.pathname = os.path.split(args.template)
        args.template = args.pathname.split(".yaml")[0]

    if args.subparser_name:
        sys.exit(locals()[args.subparser_name](args))

    sys.exit(0)
