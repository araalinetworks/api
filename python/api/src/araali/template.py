#!/usr/bin/env python
from __future__ import print_function

from . import araalictl as api
import argparse
import difflib
import glob
import json
import os
import shutil
import sys
from . import utils
import yaml

class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True

class Graph:
    def __init__(self, name):
        self.name = name

        self.node_dict = {}
        self.in_dict = {}
        self.out_dict = {}
        self.node_num = 0
        self.link_count = 0

    def add_link(self, client, server):
        client_key = yaml.dump(client)
        server_key = yaml.dump(server)
        if client_key not in self.node_dict:
            if not client.node.obj["name"]:
                client.node.obj["name"] = "node_%s" % self.node_num
            self.node_dict[client_key] = client
            self.node_num += 1
        
        if server_key not in self.node_dict:
            if not server.node.obj["name"]:
                server.node.obj["name"] = "node_%s" % self.node_num
            self.node_dict[server_key] = server
            self.node_num += 1
        
        self.out_dict.setdefault(self.node_dict[client_key].node.obj["name"],
            []).append(self.node_dict[server_key].node.obj["name"])
        
        self.in_dict.setdefault(self.node_dict[server_key].node.obj["name"],
            []).append(self.node_dict[client_key].node.obj["name"])

        self.link_count += 1
        
    def dump(self):
        basename = "%s/%s.yaml" % (utils.cfg.get("out_dir", utils.cfg["template_dir"]), self.name.replace("/", "_"))
        fname = basename

        files = glob.glob(fname+".*")
        nums = [int(a.rsplit(".", 1)[-1]) for a in files]
        if nums:
            num = 1+max(nums)
        else:
            num = 1

        fname = fname + ".%s" % num

        if os.path.isfile(basename): # yaml already exists
            os.rename(basename, fname) # backup current yaml
            if g_debug: print("backing up", basename, "to", fname)
        else:
            fname = None # we didnt need to backup

        with open(basename, "w") as f:
            yaml.dump(self, f, default_flow_style=False, default_style='', canonical=False, Dumper=NoAliasDumper)
        if g_debug: print("saving template", basename, "links:", self.link_count)

        if fname: # dont want to keep a backup if nothing changed
            with open(fname) as prev, open(basename) as curr:
                if next(difflib.unified_diff(prev.readlines(), curr.readlines()), None) == None:
                    # there is no difference, remove this one
                    os.remove(fname)
                    if g_debug: print("removing", fname, "same as", basename)

g_debug = False
def represent_graph(dumper, obj):
    value = []

    node_key = dumper.represent_data("identities")
    values = [a for a in obj.node_dict.values()]
    values.sort(key=lambda x: x.node.obj["name"])
    node_value = dumper.represent_data(values)
    value.append((node_key, node_value))

    if 0: # simple way to dump edges, to test the more optimized way below
        node_key = dumper.represent_data("edges")
        values = []
        for k,v in obj.out_dict.items():
            values.append(NameWithInOut(k, outlist=v))
        values.sort(key=lambda x: x.name)
        node_value = dumper.represent_data(values)
        value.append((node_key, node_value))

        return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

    ###
    # If it has more than one egress, we keep it, make peer ineligible
    #   if the peer is in third column, to keep things consistent. We dont
    #   want peer to sometiems be in out and sometimes be a node itself. We
    #   make it ineligible to become a node ever.
    #
    # If it has only one out, we can potentially make it "in" for some node
    #   if the peer is ineligible, we keep it
    #   if the peer has out (middle column), we remove it and keep the peer
    #     keep the peer, mark peer's peers as ineligible for in
    #   if the peer has only one in, we keep it (wont know in first pass)
    #   if the peer has multiple in, we keep the peer
    ###
    values = []
    ineligible = set() # this is a set of ineligible servers (peers)
    eligible = {}
    reevaluate = set()
    for k,v in obj.out_dict.items():
        if k in eligible: # we already took care of it
            if g_debug: print(k, "eligible", eligible)
            continue

        if len(v) > 1: # we keep it if it has more than one egress
            n = NameWithInOut(k, outlist=v)
            eligible[k] = n
            values.append(n)
            # since we consumed peer, we should always consume, even in other
            # scenarios/links - to be consistent
            for i in v:
                if i in ineligible: # it is already marked ineligible
                    continue
                if i not in obj.out_dict: # it is a pure server (3rd column)
                    if g_debug: print("for", k, "marking", i, "ineligible")
                    ineligible.add(i)
            continue

        # single peer case
        peer = v[0]
        if peer in ineligible:
            if g_debug: print("adding singleton", k, "because", peer, "ineligible")
            n = NameWithInOut(k, outlist=v)
            eligible[k] = n
            values.append(n)
            # peer is already marked ineligible
            continue

        # if peer is also a valid node with egress, we now have one ingress
        # coming into it, keep the peer
        if peer in obj.out_dict:
            # its not already added
            if peer not in eligible:
                if g_debug: print("processing singleton", k, "adding peer with egress", peer)
                n = NameWithInOut(peer, outlist=obj.out_dict[peer], inlist=[k])
                eligible[peer] = n
                values.append(n)
                for i in obj.out_dict[peer]:
                    if i not in obj.out_dict:
                        if g_debug: print("for", peer, "making", i, "ineligible")
                        ineligible.add(i)
                if peer in reevaluate:
                    reevaluate.remove(peer)
            else: # peer is already in, add me as ingress
                if g_debug: print("adding", k, "as additional ingress to existing", peer)
                eligible[peer].inlist.append(k)
        else: # peer has no egress, it might get marked ineligible
            reevaluate.add(k)

    # only single peer case need to be re-evaluated
    if g_debug: print("reevaluate", reevaluate)
    for k in reevaluate:
        peer = obj.out_dict[k][0]
        if peer in ineligible:
            values.append(NameWithInOut(k, outlist=[peer]))
        else: # peer is not ineligible
            if peer in eligible: # append to it
                eligible[peer].inlist.append(k)
            else: # adding peer for the first time
                n = NameWithInOut(peer, inlist=[k])
                eligible[peer] = n
                values.append(n)

    values.sort(key=lambda x: x.name)

    node_key = dumper.represent_data("authorizations")
    node_value = dumper.represent_data(values)
    value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

class NameWithInOut:
    def __init__(self, name, inlist=[], outlist=[]):
        self.name = name
        self.inlist = [a for a in inlist]
        self.outlist = [a for a in outlist]

def represent_name_with_in_out(dumper, obj):
    value = []

    node_key = dumper.represent_data("name")
    node_value = dumper.represent_data(obj.name)
    value.append((node_key, node_value))

    if obj.inlist:
        node_key = dumper.represent_data("in")
        obj.inlist.sort()
        node_value = dumper.represent_data(obj.inlist)
        value.append((node_key, node_value))

    if obj.outlist:
        node_key = dumper.represent_data("out")
        obj.outlist.sort()
        node_value = dumper.represent_data(obj.outlist)
        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

class NodeWithPushdown:
    def __init__(self, node, pushdown):
        self.node = node
        self.pushdown = pushdown

    def pushdown_dict(self):
        return dict([(k, self.node.obj[k]) for k in self.pushdown.obj])

def represent_node_with_pushdown(dumper, obj):
    value = []

    node_key = dumper.represent_data("node")
    node_value = dumper.represent_data(obj.node)
    value.append((node_key, node_value))

    node_key = dumper.represent_data("pushdown")
    node_value = dumper.represent_data(obj.pushdown)
    value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

class Pushdown:
    def __init__(self, obj):
        if type(obj) == dict:
            keys = [a for a in obj.keys()]
        else:
            keys = [a for a in obj]
        keys.sort()
        self.obj = keys

def represent_pushdown(dumper, obj):
    return dumper.represent_data(obj.obj)

class Node:
    def __init__(self, obj, name="__no_name__"):
        """Node is used by both node and pushdown, pushdown has no name"""
        self.obj = obj
        if name != "__no_name__":
            self.obj["name"] = name
        if "rename" in self.obj:
            self.obj["name"] = self.obj["rename"]
            del self.obj["rename"]

def represent_node(dumper, obj):
    def rank(key):
        key = key[0].value
        key_order = ["name", "dns_pattern", "subnet", "netmask", "dst_port",
                     "zone", "app", "pod", "container",
                     "binary_name", "parent_process", "process"]
        key_order = dict(zip(key_order, range(0, len(key_order))))
        return key_order[key]

    value = []
    for item_key, item_value in obj.obj.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    value.sort(key=lambda x: rank(x))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

def push(args):
    ans = input("are you sure? (yes/no)> ")
    if ans != "yes":
        print("This is a dangerous command, thanks for exercising caution!")
        return

    if args.verbose >= 1: print(args, ans)
    if args.verbose >= 1: api.g_debug = True

    basename = "%s/%s.yaml" % (utils.cfg["template_dir"], args.template)
    if not os.path.isfile(basename): # yaml already exists
        print(basename, "does not exist")
        return

    # read a sample template from araali
    obj = [a for a in api.API().get_templates(public=True, template="agent.k8s.araali_fw")[0]][0]
    # name, template, use, author, version
    if args.verbose >= 2: print(obj["name"], obj["use"], obj["author"], obj["version"])
    obj["name"] = args.template
    if args.public:
        obj["use"] = False
    else:
        obj["use"] = True
    obj["author"] = "Template As Code (Git)"
    obj["version"] = "v0.0.1"

    nodes = {}
    obj["template"] = []
    with open(basename) as f:
        template = yaml.load(f, Loader=yaml.SafeLoader)
        # load identities
        for node in template["identities"]:
            name = node["node"]["name"]
            nodes[name] = NodeWithPushdown(Node(node["node"]), Pushdown(node["pushdown"]))

        for node in template["authorizations"]:
            # name, in, out
            node_obj = nodes[node["name"]]
            if args.verbose >= 2: print(yaml.dump(node_obj))
            for label in node.get("in", []):
                peer_obj = nodes[label]
                o = {"link_filter": {}}
                o["link_filter"]["client"] = dict(peer_obj.node.obj)
                o["link_filter"]["server"] = dict(node_obj.node.obj)
                if node_obj.pushdown.obj or peer_obj.pushdown.obj:
                    o["selector_change"] = {}
                    if peer_obj.pushdown.obj:
                        o["selector_change"]["client"] = peer_obj.pushdown_dict()
                    if node_obj.pushdown.obj:
                        o["selector_change"]["server"] = node_obj.pushdown_dict()
                obj["template"].append(o)
            for label in node.get("out", []):
                peer_obj = nodes[label]
                o = {"link_filter": {}}
                o["link_filter"]["client"] = dict(node_obj.node.obj)
                o["link_filter"]["server"] = dict(peer_obj.node.obj)
                if node_obj.pushdown.obj or peer_obj.pushdown.obj:
                    o["selector_change"] = {}
                    if node_obj.pushdown.obj:
                        o["selector_change"]["client"] = node_obj.pushdown_dict()
                    if peer_obj.pushdown.obj:
                        o["selector_change"]["server"] = peer_obj.pushdown_dict()
                obj["template"].append(o)
 
    if args.verbose >= 1: print(obj)
    if args.tenant:
        tenant = args.tenant
    else:
        tenant = utils.cfg["tenant"]
    rc = api.API().update_template([obj], args.public, tenant)
    print(rc)

def alerts(args):
    if args.tenant:
        tenants = [{"name": args.tenant, "id": args.tenant}]
    elif utils.cfg.get("tenants", None):
        tenants = utils.cfg["tenants"]
        if not tenants:
            tenants = [{"name": utils.cfg["tenant"], "id": utils.cfg["tenant"]}]
        else:
            # we are doing a full run
            if not args.nopull:
                shutil.rmtree("%s/%s" % (args.progdir, ".alerts.template.py"), ignore_errors=True)
    else:
        tenants = [{"name": "account", "id": utils.cfg["tenant"]}]

    if args.nopull:
        if args.ago:
            import datetime
            def make_map(kv):
                k, v = kv.split("=")
                return k, int(v)
            ago = dict([make_map(a) for a in args.ago.split(",")])
            cutoff = datetime.datetime.now() - datetime.timedelta(**ago)
            for t in tenants:
                count = 0
                with open("%s/%s/%s.json" % (args.progdir, ".alerts.template.py", t["name"]), "r") as f:
                    for line in f:
                        line = json.loads(line)
                        # print(line.keys())
                        alert_t = datetime.datetime.fromtimestamp(int(line["timestamp"])/1000)
                        if alert_t > cutoff:
                            count += 1
                if count:
                    print("%-60s %s" % (t, count))
        else:
            print("ls .alerts.template.py/*.json | xargs wc -l")
        return

    if args.verbose >= 1: api.g_debug = True
    os.makedirs("%s/%s" % (args.progdir, ".alerts.template.py"), exist_ok=True)
    for t in tenants:
        with open("%s/%s/%s.json" % (args.progdir, ".alerts.template.py", t["name"]), "w") as f:
            count = 0
            skipped_count = 0
            token = None
            while True:
                alerts, _, _ = api.API().get_alerts(count=200000, token=token, tenant=t["id"])
                if not alerts:
                    break

                for obj in alerts:
                    if obj["alert_info"]["status"] == "CLOSE":
                        skipped_count += 1
                        continue
                    count += 1
                    json.dump(obj, f)
                    f.write("\n")

                token=obj.get("paging_token", None)
                if not token:
                    break

            print(t, "open=%s" % count, "closed=%s" % skipped_count)

def eval_drift(tenant):
    git_files = set([os.path.split(a)[1] for a in glob.glob('%s/*.yaml' % utils.cfg["template_dir"])])
    drift_files =set([os.path.split(a)[1] for a in glob.glob('%s/*.yaml' % utils.cfg["out_dir"])])

    not_in_git = list(drift_files - git_files)
    in_git = list(drift_files & git_files)
    
    not_in_git.sort()
    in_git.sort()
    
    print('\nEvaluating drift for:', tenant)
    if g_debug: print("git:", git_files, "drift:", drift_files)
    if not_in_git:
        print("*** Files not in git:")
        for f in not_in_git:
            print("\t", f)
    
    if tenant == "public":
        not_in_public = list(git_files - drift_files)
        not_in_public.sort()
        if not_in_public:
            print("*** Files not in public:")
            for f in not_in_public:
                print("\t", f)
            
    for fname in in_git:
        prevfname = utils.cfg["template_dir"] + "/" + fname
        currfname = utils.cfg["out_dir"] + "/" + fname
        with open(prevfname) as prev, open(currfname) as curr:
            if next(difflib.unified_diff(prev.readlines(), curr.readlines()), None) != None:
                print("***", prevfname, currfname, "have drifted")
            else:
                if g_debug:
                    print(prevfname, currfname, "have not drifted")


def drift(args):
    if not args.public:
        if args.tenant:
            tenants = [{"name": [a for a in utils.cfg["tenants"] if a["id"] == args.tenant][0]["name"], "id": args.tenant}]
        else:
            tenants = utils.cfg.get("tenants", None)
            if not tenants:
                tenants = [{"name": "account", "id": utils.cfg["tenant"]}]
            else:
                # full run
                if not args.nopull:
                    shutil.rmtree("%s/%s" % (args.progdir, ".drift.template.py"), ignore_errors=True)

    api.g_debug = False
    os.makedirs("%s/%s" % (args.progdir, ".drift.template.py"), exist_ok=True)

    if args.public:
        utils.cfg["out_dir"] = "%s/%s/public" % (args.progdir, ".drift.template.py")
        if not args.nopull:
            shutil.rmtree("%s/%s/public" % (args.progdir, ".drift.template.py"), ignore_errors=True)
            os.makedirs("%s/%s/public" % (args.progdir, ".drift.template.py"), exist_ok=True)
            args.tenant = None
            pull(args)
        eval_drift("public")
        return

    for t in tenants:
        utils.cfg["out_dir"] = "%s/%s/%s" % (args.progdir, ".drift.template.py", t["name"])
        if not args.nopull:
            shutil.rmtree("%s/%s/%s" % (args.progdir, ".drift.template.py", t["name"]), ignore_errors=True)
            os.makedirs("%s/%s/%s" % (args.progdir, ".drift.template.py", t["name"]), exist_ok=True)
            args.tenant = t["id"]
            pull(args)
        eval_drift("%s (%s)" % (t["name"], t["id"]))

def ls(args):
    if args.tenant:
        tenant = args.tenant
    else:
        tenant = utils.cfg["tenant"]
    for obj in api.API().get_templates(public=args.public, tenant=tenant,
                                       template=args.template)[0]:
        # keys: ['name', 'template', 'use', 'author', 'version']
        del obj["template"]
        print(obj)

def pull(args):
    if args.verbose >= 1: api.g_debug = True

    if args.tenant:
        tenant = args.tenant
    else:
        tenant = utils.cfg["tenant"]

    found = False
    for obj in api.API().get_templates(public=args.public, tenant=tenant,
                                       template=args.template)[0]:
        # get the names from local file and apply it to pulled template
        existing_nodes = {}

        basename = "%s/%s.yaml" % (utils.cfg["template_dir"], obj["name"])
        if os.path.isfile(basename): # yaml already exists
            with open(basename) as f:
                template = yaml.load(f, Loader=yaml.SafeLoader)

                # identities, authorizations
                for node in template["identities"]:
                    name = node["node"]["name"]
                    node["node"]["name"] = None
                    node = NodeWithPushdown(Node(node["node"]), Pushdown(node["pushdown"]))
                    key = yaml.dump(node)
                    existing_nodes[key] = name
 
        # keys: ['name', 'template', 'use', 'author', 'version']
        graph = Graph(obj["name"])
        for link in obj["template"]:
            #print(yaml.dump(link))

            link_filter = link["link_filter"]

            client = NodeWithPushdown(Node(link_filter["client"], None),
                        Pushdown(link.get("selector_change", {}).get("client", [])))
            server = NodeWithPushdown(Node(link_filter["server"], None),
                        Pushdown(link.get("selector_change", {}).get("server", [])))

            # fix up names based on existing nodes
            key = yaml.dump(client)
            if key in existing_nodes:
                client.node.obj["name"] = existing_nodes[key]
            else:
                print("not found", yaml.dump(client))

            key = yaml.dump(server)
            if key in existing_nodes:
                server.node.obj["name"] = existing_nodes[key]
            else:
                print("not found", yaml.dump(server))

            graph.add_link(client, server)

        graph.dump()
        found = True
    if not found:
        print("No template found")

def search(args):
    def print_non_araali_egress(a):
        if "subnet" in a["server"]["non_araali"]["server"]:
            server_ip = a["server"]["non_araali"]["server"]["subnet"]
            org = a["server"]["non_araali"]["server"].get("subnet", "None")
            print("-> %s(%s)" % (server_ip, org))
        if "dns_pattern" in a["server"]["non_araali"]["server"]:
            try:
             print("%s.%s.%s -> %s:%s" % (a["client"]["araali"]["parent_process"],
              a["client"]["araali"]["process"], a["client"]["araali"]["binary_name"],
              a["server"]["non_araali"]["server"]["dns_pattern"],
              a["server"]["non_araali"]["server"]["dst_port"]))
            except:
                print("server", yaml.dump(a))
                raise Exception("faied")
            dns = a["server"]["non_araali"]["server"]["dns_pattern"].split(":")[1:-1]
            rc = utils.run_command("ls %s/" % (utils.cfg["template_dir"]),
                    debug=g_debug, result=True, strip=False)[1].decode().strip().split("\n")
            if "saas.%s.yaml" % ".".join(dns[0].rsplit(".", 2)[-2:]) in rc:
                print("\tInstall saas.%s.yaml" % ".".join(dns[0].rsplit(".", 2)[-2:]))
            else:
                print("\t*** no template exists for saas.%s.yaml" % ".".join(dns[0].rsplit(".", 2)[-2:]))

    alerts = yaml.load(sys.stdin.read(), yaml.SafeLoader)
    for a in alerts:
        if a["alert_info"]["communication_alert_type"] == "EXTERNAL_COMMUNICATION_ATTEMPTED":
            print_non_araali_egress(a)
        elif a["alert_info"]["communication_alert_type"] == "NEW_PERIMETER_INGRESS_SERVICE":
            if args.server: # non-araali ingress
                print("-> %s.%s.%s" % (a["server"]["araali"]["parent_process"],
                    a["server"]["araali"]["process"], a["server"]["araali"]["binary_name"]))
        elif a["alert_info"]["communication_alert_type"] == "LATERAL_MOVEMENT_ATTEMPTED":
            if a["direction"] == "NON_ARAALI_EGRESS":
                print_non_araali_egress(a)
            else: # araali
                print("%s.%s.%s -> %s.%s%s" % (a["client"]["araali"]["parent_process"],
                  a["client"]["araali"]["process"], a["client"]["araali"]["binary_name"],
                  a["server"]["araali"]["parent_process"],
                  a["server"]["araali"]["process"], a["server"]["araali"]["binary_name"]))
        else:
            print("server", yaml.dump(a))
            raise Exception("unhandled: %s" % a["alert_info"]["communication_alert_type"])

def fmt(args):
    if args.verbose >= 1: print(args.template, args.dirname)
    graph = Graph(args.template)
    nodes = {}
    with open("%s/%s.yaml" % (args.dirname, args.template)) as f:
        template = yaml.load(f, Loader=yaml.SafeLoader)

        # identities, authorizations
        for node in template["identities"]:
            name = node["node"]["name"]
            nodes[name] = NodeWithPushdown(Node(node["node"]),
                                                   Pushdown(node["pushdown"]))
        for link in template["authorizations"]:
            for l in link.get("in", []):
                graph.add_link(nodes[l], nodes[link["name"]])
            for l in link.get("out", []):
                graph.add_link(nodes[link["name"]], nodes[l])
    graph.dump()

yaml.add_representer(Node, represent_node)
yaml.add_representer(Pushdown, represent_pushdown)
yaml.add_representer(NodeWithPushdown, represent_node_with_pushdown)
yaml.add_representer(Graph, represent_graph)
yaml.add_representer(NameWithInOut, represent_name_with_in_out)
