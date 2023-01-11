"""Used to execute modeule from the command line
    Fetches alerts and prints the count
"""
from __future__ import print_function

import argparse
import boto3
import datetime
import time
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
from . import aws as _aws

def tenant(args):
    if args.tenant_subparser_name == "delete":
        print(API().delete_tenant(tenant=args.tenant))

def lens(args):
    if args.set:
        if args.set in ["enforce", "unenforce"]:
            op = {"enforce": "ADD", "unenforce": "DEL"}[args.set]
            if args.svc:
                sp = args.svc.split(":")
                assert len(sp) == 2, "svc format is service:port"
                args.svc, args.svc_port = sp
            else:
                args.svc_port = None
            API().set_enforced(op, args.zone, args.app, args.pod,
                args.container, args.process, args.parent, args.binpath,
                args.svc, args.svc_port, args.tenant)
    else: # get
        filterby = []
        if args.zone: filterby.append("lens.zone=%s" % args.zone)
        if args.app: filterby.append("lens.app=%s" % args.app)
        if args.pod: filterby.append("lens.pod=%s" % args.pod)
        if args.container: filterby.append("lens.container_name=%s" % args.container)
        if args.process: filterby.append("lens.process=%s" % args.process)
        if args.parent: filterby.append("lens.parent_process=%s" % args.parent)
        if args.binpath: filterby.append("lens.binary_name=%s" % args.binpath)
        utils.dump_table(API().get_enforced(args.tenant)[0], filterby=None if filterby == [] else ":".join(filterby))

def podmap(args):
    if args.podmap_subparser_name == "list":
        links, status = API().get_pod_mapping(args.zone, tenant=args.tenant)
        if status == 0:
            print("Got %s mapping entries" % len(links))

            if not args.countby: args.countby = "translated_pod_name"
            utils.dump_table(links,
                         quiet=args.quiet, filterby=args.filterby,
                         countby=args.countby, groupby=args.groupby)
    elif args.podmap_subparser_name == "add":
        links, status = API().add_pod_mapping(args.zone, args.app, args.pattern, args.name, tenant=args.tenant)
    elif args.podmap_subparser_name == "del":
        links, status = API().del_pod_mapping(args.zone, args.app, args.pattern, args.name, tenant=args.tenant)

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
        tracking = [a for a in utils.cfg.get("tenants", [])]
        tracking_ids = [a["id"] for a in tracking]
        obj = araalictl.API().get_tenants()[0]["subtenantlist"]
        # ['tenantid', 'adminemail', 'activevmcount', 'activecontainercount', 'perimeteralertcount', 'homealertcount', 'lastsignedin']
        print("     %-22s %-42s %-7s %-10s %s" % ("tenant-id", "admin-email", "count", "tracked", "last-signed-in"))
        agent_count = 0
        for i, o in enumerate(obj):
            o["lastsignedin"] = datetime.datetime.fromtimestamp(o["lastsignedin"]/1000) if o["lastsignedin"] else ""
            print("%3s: t=%-20s e=%-40s c=%-5s tr=%-7s s=%s" % (i+1, o["tenantid"],
                o["adminemail"], o["activevmcount"], o["tenantid"] in tracking_ids,
                o["lastsignedin"] if o["lastsignedin"] else "nil"))
            agent_count += o["activevmcount"]
            tracking = [a for a in tracking if o["tenantid"] != a["id"]]
        print("Total agents: %s" % agent_count)
        if tracking:
            print("\n=== Tracking but not active ===")
            for i, t in enumerate(tracking):
                print("%3s: t=%-20s n=%s" % (i, t["id"], t["name"]))
        return
    return utils.config(args.tenant, args.tenants, args.template_dir, args.backend)

def alerts(args):
    alerts, page, status = API().get_alerts(args.count, args.ago,
            closed_alerts=args.closed, all_alerts=args.all, tenant=args.tenant)
    day_dict = {}
    local_zone = tz.tzlocal()
    if status == 0:
        if args.dump_csv:
            for line in utils.dump_csv(alerts):
                print(line)
        elif args.dump_yaml:
            if args.flatten:
                print(yaml.dump(list(utils.flatten_table(alerts))))
            else:
                print(yaml.dump(alerts))
        else:
            print("Got %s alerts" % len(alerts))
            if args.countby is None: args.countby = "unique_id"
            utils.dump_table(alerts,
                         quiet=args.quiet, filterby=args.filterby,
                         countby=args.countby, groupby=args.groupby, flatten=args.flatten)

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
    for k in ["zone", "app"]:
        if k not in filters:
            filters[k] = ".*"

    search_type = "asset" # container, app/VM
    filter_keys = set(filters.keys())
    if set(["process", "binary_name", "parent_process"]) & filter_keys:
        search_type = "workload" # process lens
        if 0:
            for k in ["process", "binary_name", "parent_process"]:
                if k not in filters:
                    filters[k] = ".*"
    elif set(["dns_pattern", "dst_port"]) & filter_keys:
        search_type = "service" # service lens
        if 0:
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

                if 0 and search_type == "asset":
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
                    if search_type == "asset":
                        nfilters = dict([a for a in filters.items()])

                        capp = client.get("app", "").split(".")
                        if len(capp) == 3:
                            client["app"] = capp[0]
                            client["pod"] = capp[1]
                            client["container"] = capp[2]

                        sapp = server.get("app", "").split(".")
                        if len(sapp) == 3:
                            server["app"] = sapp[0]
                            server["pod"] = sapp[1]
                            server["container"] = sapp[2]

                        client_m = match_filters(nfilters, client)
                        server_m = match_filters(nfilters, server)
                        if client_m:
                            wkey = [str(client[k]) for k in filters.keys()]
                            wkey = ":".join(wkey)
                            if wkey not in workload_dict:
                                print("="*40, i, "="*40)
                                i += 1
                                print(yaml.dump(client))
                                workload_dict[wkey] = 1
                            else:
                                workload_dict[wkey] += 1
                        
                        if server_m:
                            wkey = [str(server[k]) for k in filters.keys()]
                            wkey = ":".join(wkey)
                            if wkey not in workload_dict:
                                print("="*40, i, "="*40)
                                i += 1
                                print(yaml.dump(server))
                                workload_dict[wkey] = 1
                            else:
                                workload_dict[wkey] += 1

                    elif search_type == "workload":
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
    if args.nanny:
        print(api.API().get_helm_values(workload_name=args.zone,
                                        tenant=args.tenant,
                                        nanny=args.nanny))
    else:
        print(yaml.dump(araalictl.API().get_helm_values(
            args.zone, args.tenant)[0]))

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
    if remaining and remaining[0] not in ["authorize", "config"]:
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

    return subprocess.call(" ".join(prepend + [api.cmdline] + remaining), shell=True)

def template(args):
    if args.t_subparser_name:
        return getattr(module_template, args.t_subparser_name)(args)

def fw_config(args):
    if not args.zone or not args.tenant:
        print("*** please specify both zone and tenant")
        return

    if args.update:
        status = api.API().update_fw_config(zone=args.zone,
                                            tenant=args.tenant,
                                            data_file_location=args.update)
        print(status)
        return

    knobs = api.API().get_fw_config(zone=args.zone, tenant=args.tenant)
    print(yaml.dump(knobs))

def quickstart(args):
    # TODO(rsn): Till we handle subtenants properly, maybe add a check for whether user exists at this point itself
    timestamp_str = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
    if args.quickstart_subparser_name == "vm":
        success, result = _aws.cf_launch_fortified_vm(stack_name="araaliapicf-quickstart-vm-stack-%s" % timestamp_str, email=args.email, key_pair=args.key, ami_id=args.ami)
        if not success:
            print("Error: Quickstart setup failed, message: %s"%result)
            sys.exit(1)
        else:
            print(result)
    elif args.quickstart_subparser_name == "eks":
        eks_client = boto3.client('eks')
        EKS_STACK_NAME = "araaliapicfg-quickstart-stack-%s" % timestamp_str
        EKS_CLUSTER_NAME = "araaliapicfg-quickstart-eks-%s" % timestamp_str
        cluster_name = args.name
        launch_cluster = True
        if cluster_name == None or cluster_name == "":
            launch_cluster = True
            cluster_name = EKS_CLUSTER_NAME
        else:
            # Check if cluster exists
            response = eks_client.list_clusters()
            if "clusters" not in response:
                print("Error: list_clusters returned invalid response")  
                sys.exit(1)  
            launch_cluster = cluster_name not in response["clusters"]
        # Launch cluster is requested
        if launch_cluster:
            success, result = _aws.cf_launch_eks_cluster(stack_name=EKS_STACK_NAME, cluster_name=cluster_name, availability_zones=args.availabilityzones)
            if not success:
                print("Error: Quickstart EKS cluster setup failed")
                sys.exit(1)
            # Wait until cluster is set up
            counter = 0
            while(True):
                if counter % 10 == 0:
                    print("Waiting for cluster create - %d/120" %counter)
                if _aws.cf_validate_stack_creation(EKS_STACK_NAME):
                    break
                if counter >= 120:
                    print("Error: Quickstart EKS cluster setup failed")
                    sys.exit(1)
                counter += 1
                time.sleep(30)
        # Update kubeconfig to point to newly created cluster and fetch ARN
        utils.update_kubeconfig(cluster_name)
        response = eks_client.describe_cluster(name=cluster_name)
        if "cluster" not in response and "arn" not in response["cluster"]:
            sys.exit(1)
        cluster_arn = response["cluster"]["arn"]
        # Install Helm on machine if not present
        # Verify if Helm is present on machine
        rc = utils.run_command("which helm", debug=False, result=True, strip=False)
        if rc[0]:
            # Helm is not present. Download Helm on machine
            success, _ = utils.run_command_logfailure("curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3")
            if not success:
                sys.exit(1)
            success, _ = utils.run_command_logfailure("chmod 700 get_helm.sh")
            if not success:
                sys.exit(1)
            success, _ = utils.run_command_logfailure("./get_helm.sh")
            if not success:
                sys.exit(1)
        # Run helm install command
        success, _ = utils.run_command_logfailure("helm repo add araali-helm https://araalinetworks.github.io/araali-helm/")
        if not success:
            sys.exit(1)
        success, _ = utils.run_command_logfailure("helm install araali-quickstart-nanny --set email=%s araali-helm/araali-quickstartnanny --kube-context=%s" % (args.email, cluster_arn))
        if not success:
            sys.exit(1)
    print("Quickstart initialized successfully...")

def aws(args):
    if args.aws_subparser_name == "cf":
        if args.aws_cf_subparser_name == "ls":
            if args.countby is None:
                args.countby = "id,name"
            utils.dump_table(_aws.cf_ls(args.all),
                         quiet=args.quiet, filterby=args.filterby,
                         countby=args.countby, groupby=args.groupby)
        elif args.aws_cf_subparser_name == "add":
            if args.aws_cf_add_subparser_name == "vm":
                _aws.cf_add_vm()
        elif args.aws_cf_subparser_name == "rm":
            _aws.cf_rm(args.name)

    elif args.aws_subparser_name == "assets":
        # account vpc subnet type image platform state public_ip
        if args.countby is None:
            args.countby = "instance_id,account,vpc,subnet"
        utils.dump_table(_aws.assets(args.members),
                         quiet=args.quiet, filterby=args.filterby,
                         countby=args.countby, groupby=args.groupby)

if __name__ == "__main__":
    top_parser = argparse.ArgumentParser(description = 'Araali Python CLI')
    top_parser.add_argument('--verbose', '-v', action='count', default=0, help="specify multiple times to increase verbosity (-vvv)")
    top_parser.add_argument('--use_api', '-u', action='store_true', help="user api instead of araalictl")
    top_subparsers = top_parser.add_subparsers(dest="subparser_name")

    parser_cmd = top_subparsers.add_parser("lens", help="show/manipulate application lenses")
    parser_opt = parser_cmd.add_argument("-t", "--tenant", help="lenses for a specific tenant")
    parser_opt = parser_cmd.add_argument("-z", "--zone", help="zone for the lens")
    parser_opt = parser_cmd.add_argument("-a", "--app", help="app for the lens")
    parser_opt = parser_cmd.add_argument("-p", "--pod", help="pod for the lens")
    parser_opt = parser_cmd.add_argument("-c", "--container", help="container for the lens")
    parser_opt = parser_cmd.add_argument("--process", help="process for the lens")
    parser_opt = parser_cmd.add_argument("--parent", help="parent process for the lens")
    parser_opt = parser_cmd.add_argument("--binpath", help="binary path for the lens")
    parser_opt = parser_cmd.add_argument("-s", "--svc", help="service for the lens")
    parser_opt = parser_cmd.add_argument("-S", "--set",
            choices=["enforce", "unenforce"],
            help="service for the lens")

    parser_cmd = top_subparsers.add_parser("podmap", help="pod name mapping configuration")
    subparsers = parser_cmd.add_subparsers(dest="podmap_subparser_name")

    parser_subcmd = subparsers.add_parser("add", help="add a new mapping")
    parser_subcmd.add_argument('-t', '--tenant', help="pod mapping for a specific tenant")
    parser_subcmd.add_argument('-z', '--zone', help="zone")
    parser_subcmd.add_argument('-a', '--app', help="app")
    parser_subcmd.add_argument('-p', '--pattern', help="pattern")
    parser_subcmd.add_argument('-n', '--name', help="name")

    parser_subcmd = subparsers.add_parser("del", help="add a new mapping")
    parser_subcmd.add_argument('-t', '--tenant', help="pod mapping for a specific tenant")
    parser_subcmd.add_argument('-z', '--zone', help="zone")
    parser_subcmd.add_argument('-a', '--app', help="app")
    parser_subcmd.add_argument('-p', '--pattern', help="pattern")
    parser_subcmd.add_argument('-n', '--name', help="name")

    parser_subcmd = subparsers.add_parser("list", help="list pod mappings")
    parser_subcmd.add_argument('-t', '--tenant', help="pod mapping for a specific tenant")
    parser_subcmd.add_argument('-z', '--zone', help="zone")
    parser_subcmd.add_argument("-q", "--quiet", action="store_true", help="count by unique values")
    parser_subcmd.add_argument("-c", "--countby", help="count by unique values")
    parser_subcmd.add_argument("-g", "--groupby", help="groub by (key)")
    parser_subcmd.add_argument("-f", "--filterby", help="filter by (key)")

    parser_config = top_subparsers.add_parser("config", help="list/change config params")
    parser_config.add_argument('-t', '--tenant', help="setup sub-tenant param (sticky)")
    parser_config.add_argument('--tenants', help="setup a list of sub-tenants (for managing alerts)")
    parser_config.add_argument('--backend', help="setup a custom backend (internal unit testing)")
    parser_config.add_argument('-g', '--get_tenants', action="store_true", help="get active tenants")
    parser_config.add_argument('-d', '--template_dir', help="custom template directory")

    parser_alerts = top_subparsers.add_parser("alerts", help="get alerts (to create templates for)")
    parser_alerts.add_argument('-t', '--tenant', help="get alert for a specific tenant")
    parser_alerts.add_argument('--closed', action="store_true", help="get closed alerts")
    parser_alerts.add_argument('--all', action="store_true", help="get all alerts (disregard subscription)")
    parser_alerts.add_argument('-n', '--nopull', action="store_true", help="dont pull from araali")
    parser_alerts.add_argument('-C', '--count', type=int, help="dont pull from araali")
    parser_alerts.add_argument("-q", "--quiet", action="store_true", help="count by unique values")
    parser_alerts.add_argument("-c", "--countby", help="count by unique values")
    parser_alerts.add_argument("-g", "--groupby", help="groub by (key)")
    parser_alerts.add_argument("-f", "--filterby", help="filter by (key)")
    parser_alerts.add_argument("-F", "--flatten", action="store_true", help="flatten the yaml object")
    parser_alerts.add_argument("--dump_yaml", action="store_true", help="dump yaml for saving output")
    parser_alerts.add_argument("--dump_csv", action="store_true", help="dump csv for saving output")
    parser_alerts.add_argument('--ago', help="lookback")

    parser_insights = top_subparsers.add_parser("insights", help="get insights")
    parser_insights.add_argument('-t', '--tenant', help="get insights for a specific tenant")
    parser_insights.add_argument('-z', '--zone', help="insights for a specific zone")

    parser_assets = top_subparsers.add_parser("assets", help="get assets")
    parser_assets.add_argument('-t', '--tenant', help="get assets for a specific tenant")
    parser_assets.add_argument('-z', '--zone', help="assets for a specific zone")
    parser_assets.add_argument('-a', '--app', help="links for a specific app")
    parser_assets.add_argument('-n', '--nopull', action="store_true", help="dont pull from araali")
    parser_assets.add_argument('-f', '--filters', help="query filters. eg: zone=.*,app=.*,cve_sev=4,cve_count=^0$")
    parser_assets.add_argument('--ago', help="lookback")

    parser_token = top_subparsers.add_parser("token", help="manage api tokens")
    parser_token.add_argument('-t', '--tenant', help="token management for a specific tenant")
    parser_token.add_argument('-a', '--add', help="create new token")
    parser_token.add_argument('-d', '--delete', help="delete token by name")
    parser_token.add_argument('-e', '--email', help="user email")
    parser_token.add_argument('-l', '--list', action="store_true", help="list all tokens")

    parser_cmd = top_subparsers.add_parser("tenant", help="tenant management")
    subparsers = parser_cmd.add_subparsers(dest="tenant_subparser_name")
    parser_cmd = subparsers.add_parser("delete", help="delete tenant")
    parser_cmd.add_argument('-t', '--tenant', help="tenant id to delete")

    parser_links = top_subparsers.add_parser("links", help="get links")
    parser_links.add_argument('-t', '--tenant', help="get links for a specific tenant")
    parser_links.add_argument('-z', '--zone', help="links for a specific zone")
    parser_links.add_argument('-a', '--app', help="links for a specific app")
    parser_links.add_argument('-s', '--svc', help="links for a specific svc")
    parser_links.add_argument('--ago', help="lookback")

    parser_za = top_subparsers.add_parser("search", help="search assets, workloads, services")
    parser_za.add_argument('-t', '--tenant', help="get zones and apps for a specific tenant")
    parser_za.add_argument('-n', '--nopull', action="store_true", help="dont pull from araali")
    parser_za.add_argument('-f', '--filters', help="query filters. eg: zone=.*,app=.*,pod=.*,container=.* process=.*,binary_name=.*,parent_process=.*,dns_pattern=.*,dst_port=.*")

    parser_helm = top_subparsers.add_parser("helm", help="generate values for araaly firewall helm chart")
    parser_helm.add_argument('-t', '--tenant', help="helm chart for a specific tenant")
    parser_helm.add_argument('-z', '--zone', help="helm for a specific zone")
    parser_helm.add_argument('-n', '--nanny', action="store_true", help="helm chart for nanny or firewall")

    parser_fw_config = top_subparsers.add_parser(
        "fw_config", help="modify araali fw config on the backend")
    parser_fw_config.add_argument(
        '-g', '--get', action="store_true", help="get the current config")
    parser_fw_config.add_argument(
        '-u', '--update', help="update with json in specified file location")
    parser_fw_config.add_argument(
        '-t', '--tenant', help="fw config for a specific tenant")
    parser_fw_config.add_argument(
        '-z', '--zone', help="fw config for a specific zone")

    parser_ctl = top_subparsers.add_parser("ctl", help="run araalictl commands")

    parser_quickstart = top_subparsers.add_parser("quickstart", help="Launch Araali Quickstart")
    quickstart_subparsers = parser_quickstart.add_subparsers(dest="quickstart_subparser_name")

    parser_quickstart_vm = quickstart_subparsers.add_parser("vm", help="Launch Araali VM quickstart")
    parser_quickstart_vm.add_argument('-e', '--email', help="email of quickstart user")
    parser_quickstart_vm.add_argument('-k', '--key', help="ssh key to use")
    parser_quickstart_vm.add_argument('-a', '--ami', help="ami ID of VM to be launched")

    parser_quickstart_eks = quickstart_subparsers.add_parser("eks", help="Launch Araali Quickstart for EKS")
    parser_quickstart_eks.add_argument('-e', '--email', help="email of quickstart user")
    parser_quickstart_eks.add_argument('-n', '--name', default="", help="name of quickstart EKS cluster")
    parser_quickstart_eks.add_argument('-a', '--availabilityzones', default=["us-west-2a", "us-west-2b"], help="Availability Zones within Region to deploy Araali quickstart")

    parser_aws = top_subparsers.add_parser("aws", help='aws utilities')
    aws_subparsers = parser_aws.add_subparsers(dest="aws_subparser_name")

    parser_aws_cf = aws_subparsers.add_parser("cf", help="cloudformation management")
    aws_cf_subparsers = parser_aws_cf.add_subparsers(dest="aws_cf_subparser_name")

    parser_command = aws_cf_subparsers.add_parser("ls", help="list managed cf stacks")
    parser_opt = parser_command.add_argument("-a", "--all", action="store_true", help="all cloudformation stacks")
    parser_opt = parser_command.add_argument("-q", "--quiet", action="store_true", help="count by unique values")
    parser_opt = parser_command.add_argument("-c", "--countby", help="count by unique values")
    parser_opt = parser_command.add_argument("-g", "--groupby", help="groub by (key)")
    parser_opt = parser_command.add_argument("-f", "--filterby", help="filter by (key)")

    parser_command = aws_cf_subparsers.add_parser("add", help="add new cf stack")
    subparsers = parser_command.add_subparsers(dest="aws_cf_add_subparser_name")

    parser_command = subparsers.add_parser("vm", help="add araali protected VM")

    parser_command = aws_cf_subparsers.add_parser("rm", help="rm cf stack")
    parser_opt = parser_command.add_argument("name", help="name of araali managed cloudformation template")

    parser_command = aws_subparsers.add_parser("assets", help="asset management")
    parser_opt = parser_command.add_argument("-m", "--members", action="store_true", help="scan members")
    parser_opt = parser_command.add_argument("-q", "--quiet", action="store_true", help="count by unique values")
    parser_opt = parser_command.add_argument("-c", "--countby", help="count by unique values")
    parser_opt = parser_command.add_argument("-g", "--groupby", help="groub by (key)")
    parser_opt = parser_command.add_argument("-f", "--filterby", help="filter by (key)")

    parser_template = top_subparsers.add_parser("template", help='Manage Templates as Code (in Git)')
    top_parser.add_argument('-T', '--template', help="apply operation for a specific template")

    t_subparsers = parser_template.add_subparsers(dest="t_subparser_name")

    parser_alerts = t_subparsers.add_parser("search", help="search for match in existing templates")
    parser_alerts.add_argument('-s', '--server', help="show exposed servers")

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

    args, remaining = top_parser.parse_known_args()
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
