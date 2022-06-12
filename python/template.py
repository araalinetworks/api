#!/usr/bin/env python
"""
    Usage:
        ./setup.sh
        ./template.py pull -t control |less
        ./template.py pull -p -t agent.k8s.araali_fw|less
        ./template.py fmt ../templates/control.yaml.1
"""
import araalictl
import argparse
import difflib
import glob
import json
import os
import shutil
import sys
import yaml

class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True

cfg_fname = os.environ['HOME']+"/.araali_templates.cfg"

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
        global cfg
        basename = "%s/%s.yaml" % (cfg.get("out_dir", cfg["template_dir"]), self.name)
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
            if args.verbose >= 0: print("backing up", basename, "to", fname)
        else:
            fname = None # we didnt need to backup

        with open(basename, "w") as f:
            yaml.dump(self, f, default_flow_style=False, default_style='', canonical=False, Dumper=NoAliasDumper)
        if args.verbose >= 0: print("saving template", basename, "links:", self.link_count)

        if fname: # dont want to keep a backup if nothing changed
            with open(fname) as prev, open(basename) as curr:
                if next(difflib.unified_diff(prev.readlines(), curr.readlines()), None) == None:
                    # there is no difference, remove this one
                    os.remove(fname)
                    if args.verbose >= 0: print("removing", fname, "same as", basename)

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
            if args.verbose >= 3: print(k, "eligible", eligible)
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
                    if args.verbose >= 1: print("for", k, "marking", i, "ineligible")
                    ineligible.add(i)
            continue

        # single peer case
        peer = v[0]
        if peer in ineligible:
            if args.verbose >= 1: print("adding singleton", k, "because", peer, "ineligible")
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
                if args.verbose >= 1: print("processing singleton", k, "adding peer with egress", peer)
                n = NameWithInOut(peer, outlist=obj.out_dict[peer], inlist=[k])
                eligible[peer] = n
                values.append(n)
                for i in obj.out_dict[peer]:
                    if i not in obj.out_dict:
                        if args.verbose >= 1: print("for", peer, "making", i, "ineligible")
                        ineligible.add(i)
                if peer in reevaluate:
                    revaluate.remove(peer)
            else: # peer is already in, add me as ingress
                if args.verbose >= 1: print("adding", k, "as additional ingress to existing", peer)
                eligible[peer].inlist.append(k)
        else: # peer has no egress, it might get marked ineligible
            reevaluate.add(k)

    # only single peer case need to be re-evaluated
    if args.verbose >= 1: print("reevaluate", reevaluate)
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
        # XXX: temporary workaround - remove ^$ from binary_name, process etc
        if self.pushdown.obj:
            for k,v in self.pushdown.obj.items():
                if v[0] == "^":
                    self.pushdown.obj[k] = v[1:-1] # strip ^ and $
                elif v[0:3] == ".*:":
                    self.pushdown.obj[k] = v[3:-3] # strip .*: and :.*

def represent_node_with_pushdown(dumper, obj):
    value = []

    node_key = dumper.represent_data("node")
    node_value = dumper.represent_data(obj.node)
    value.append((node_key, node_value))

    node_key = dumper.represent_data("pushdown")
    node_value = dumper.represent_data(obj.pushdown)
    value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

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
    global cfg
    ans = input("are you sure? (yes/no)> ")
    if ans != "yes":
        print("This is a dangerous command, thanks for exercising caution!")
        return

    if args.verbose >= 1: print(args, ans)
    if args.verbose >= 1: araalictl.g_debug = True

    basename = "%s/%s.yaml" % (cfg["template_dir"], args.template)
    if not os.path.isfile(basename): # yaml already exists
        print(basename, "does not exist")
        return

    # read a sample template from araali
    obj = [a for a in araalictl.fetch_templates(public=True, template="agent.k8s.araali_fw")][0]
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
            nodes[name] = NodeWithPushdown(Node(node["node"]), Node(node["pushdown"]))

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
                        o["selector_change"]["client"] = dict(peer_obj.pushdown.obj)
                    if node_obj.pushdown.obj:
                        o["selector_change"]["server"] = dict(node_obj.pushdown.obj)
                obj["template"].append(o)
            for label in node.get("out", []):
                peer_obj = nodes[label]
                o = {"link_filter": {}}
                o["link_filter"]["client"] = dict(node_obj.node.obj)
                o["link_filter"]["server"] = dict(peer_obj.node.obj)
                if node_obj.pushdown.obj or peer_obj.pushdown.obj:
                    o["selector_change"] = {}
                    if node_obj.pushdown.obj:
                        o["selector_change"]["client"] = dict(node_obj.pushdown.obj)
                    if peer_obj.pushdown.obj:
                        o["selector_change"]["server"] = dict(peer_obj.pushdown.obj)
                obj["template"].append(o)
 
    if args.verbose >= 1: print(obj)
    if args.tenant:
        tenant = args.tenant
    else:
        tenant = cfg["tenant"]
    rc = araalictl.update_template([obj], args.public, tenant)
    print(rc)

def alerts(args):
    global cfg

    if args.tenant:
        tenants = [{"name": args.tenant, "id": args.tenant}]
    else:
        tenants = cfg["tenants"]
        if not tenants:
            tenants = [{"name": cfg["tenant"], "id": cfg["tenant"]}]
        else:
            # we are doing a full run
            if not args.nopull:
                shutil.rmtree("%s/%s" % (args.progdir, ".alerts.template.py"), ignore_errors=True)

    if args.nopull:
        print("ls .alerts.template.py/*.json | xargs wc -l")
        return

    if args.verbose >= 1: araalictl.g_debug = True
    os.makedirs("%s/%s" % (args.progdir, ".alerts.template.py"), exist_ok=True)
    for t in tenants:
        with open("%s/%s/%s.json" % (args.progdir, ".alerts.template.py", t["name"]), "w") as f:
            count = 0
            skipped_count = 0
            token = None
            while True:
                for obj in araalictl.alerts(start_time=0, end_time=0, token=token, count=200000, tenant=t["id"]):
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
    global cfg

    git_files = set([os.path.split(a)[1] for a in glob.glob('%s/*.yaml' % cfg["template_dir"])])
    drift_files =set([os.path.split(a)[1] for a in glob.glob('%s/*.yaml' % cfg["out_dir"])])

    not_in_git = list(drift_files - git_files)
    in_git = list(drift_files & git_files)
    
    not_in_git.sort()
    in_git.sort()
    
    print('\nEvaluating drift for:', tenant)
    if args.verbose >= 3: print("git:", git_files, "drift:", drift_files)
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
        prevfname = cfg["template_dir"] + "/" + fname
        currfname = cfg["out_dir"] + "/" + fname
        with open(prevfname) as prev, open(currfname) as curr:
            if next(difflib.unified_diff(prev.readlines(), curr.readlines()), None) != None:
                print("***", prevfname, currfname, "have drifted")
            else:
                if args.verbose >= 1:
                    print(prevfname, currfname, "have not drifted")


def drift(args):
    global cfg

    if args.tenant:
        tenants = [{"name": [a for a in cfg["tenants"] if a["id"] == args.tenant][0]["name"], "id": args.tenant}]
    else:
        tenants = cfg["tenants"]
        if not tenants:
            tenants = [{"name": [a for a in cfg["tenants"] if a["id"] == cfg["tenant"]][0]["name"], "id": cfg["tenant"]}]
        else:
            # full run
            if not args.nopull:
                shutil.rmtree("%s/%s" % (args.progdir, ".drift.template.py"), ignore_errors=True)

    araalictl.g_debug = False
    os.makedirs("%s/%s" % (args.progdir, ".drift.template.py"), exist_ok=True)

    if args.public:
        cfg["out_dir"] = "%s/%s/public" % (args.progdir, ".drift.template.py")
        if not args.nopull:
            shutil.rmtree("%s/%s/public" % (args.progdir, ".drift.template.py"), ignore_errors=True)
            os.makedirs("%s/%s/public" % (args.progdir, ".drift.template.py"), exist_ok=True)
            args.tenant = None
            pull(args)
        eval_drift("public")
        return

    for t in tenants:
        cfg["out_dir"] = "%s/%s/%s" % (args.progdir, ".drift.template.py", t["name"])
        if not args.nopull:
            shutil.rmtree("%s/%s/%s" % (args.progdir, ".drift.template.py", t["name"]), ignore_errors=True)
            os.makedirs("%s/%s/%s" % (args.progdir, ".drift.template.py", t["name"]), exist_ok=True)
            args.tenant = t["id"]
            pull(args)
        eval_drift("%s (%s)" % (t["name"], t["id"]))

def ls(args):
    global cfg

    if args.tenant:
        tenant = args.tenant
    else:
        tenant = cfg["tenant"]
    for obj in araalictl.fetch_templates(public=args.public, tenant=tenant,
                                       template=args.template):
        # keys: ['name', 'template', 'use', 'author', 'version']
        del obj["template"]
        print(obj)

def pull(args):
    global cfg

    if args.verbose >= 1: araalictl.g_debug = True

    if args.tenant:
        tenant = args.tenant
    else:
        tenant = cfg["tenant"]

    found = False
    for obj in araalictl.fetch_templates(public=args.public, tenant=tenant,
                                       template=args.template):
        # get the names from local file and apply it to pulled template
        existing_nodes = {}

        basename = "%s/%s.yaml" % (cfg["template_dir"], obj["name"])
        if os.path.isfile(basename): # yaml already exists
            with open(basename) as f:
                template = yaml.load(f, Loader=yaml.SafeLoader)

                # identities, authorizations
                for node in template["identities"]:
                    name = node["node"]["name"]
                    node["node"]["name"] = None
                    node = NodeWithPushdown(Node(node["node"]), Node(node["pushdown"]))
                    key = yaml.dump(node)
                    existing_nodes[key] = name
 
        # keys: ['name', 'template', 'use', 'author', 'version']
        graph = Graph(obj["name"])
        for link in obj["template"]:
            #print(yaml.dump(link))

            link_filter = link["link_filter"]

            client = NodeWithPushdown(Node(link_filter["client"], None),
                        Node(link.get("selector_change", {}).get("client", {})))
            server = NodeWithPushdown(Node(link_filter["server"], None),
                        Node(link.get("selector_change", {}).get("server", {})))

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
                                                   Node(node["pushdown"]))
        for link in template["authorizations"]:
            for l in link.get("in", []):
                graph.add_link(nodes[l], nodes[link["name"]])
            for l in link.get("out", []):
                graph.add_link(nodes[link["name"]], nodes[l])
    graph.dump()

if __name__ == '__main__':
    cfg = read_config()
    parser = argparse.ArgumentParser(description = 'Manage Templates as Code (in Git)')
    parser.add_argument('--verbose', '-v', action='count', default=0, help="specify multiple times to increase verbosity (-vvv)")
    parser.add_argument('-T', '--template', help="apply operation for a specific template")
    subparsers = parser.add_subparsers(dest="subparser_name")

    parser_alerts = subparsers.add_parser("alerts", help="get alerts (to create templates for)")
    parser_alerts.add_argument('-t', '--tenant', help="get alert for a specific tenant")
    parser_alerts.add_argument('-n', '--nopull', action="store_true", help="dont pull from araali")
    
    parser_drift = subparsers.add_parser("drift", help="get drift (from template as code)")
    parser_drift.add_argument('-t', '--tenant', help="get drift for a specific tenant")
    parser_drift.add_argument('-p', '--public', action="store_true", help="drift in public library")
    parser_drift.add_argument('-n', '--nopull', action="store_true", help="dont pull from araali")
    parser_drift.add_argument('-T', '--template', help="get drift for a specific template (name or path)")
    
    parser_list = subparsers.add_parser("ls", help="list templates")
    parser_list.add_argument('-p', '--public', action="store_true", help="list from public library")
    parser_list.add_argument('-t', '--tenant', help="list for a sub-tenant")
    parser_list.add_argument('-T', '--template', help="list a specific template (name or path)")
    
    parser_pull = subparsers.add_parser("pull", help="pull templates")
    parser_pull.add_argument('-p', '--public', action="store_true", help="pull from public library")
    parser_pull.add_argument('-T', '--template', help="pull a specific template (name or path)")
    parser_pull.add_argument('-t', '--tenant')
    
    parser_push = subparsers.add_parser("push", help="push templates")
    parser_push.add_argument('-p', '--public', action="store_true", help="push to public library")
    parser_push.add_argument('-T', '--template', help="push a specific template (name or path)")
    parser_push.add_argument('-t', '--tenant', help="push for a sub-tenant")
    
    parser_config = subparsers.add_parser("config", help="list/change config params")
    parser_config.add_argument('-t', '--tenant', help="setup sub-tenant param (sticky)")
    parser_config.add_argument('--tenants', help="setup a list of sub-tenants (for managing alerts)")
    parser_config.add_argument('-d', '--template_dir', help="custom template directory")

    parser_format = subparsers.add_parser("fmt", help="rename template node name/ format into a normalized form")
    parser_format.add_argument('template')

    yaml.add_representer(Node, represent_node)
    yaml.add_representer(NodeWithPushdown, represent_node_with_pushdown)
    yaml.add_representer(Graph, represent_graph)
    yaml.add_representer(NameWithInOut, represent_name_with_in_out)

    args = parser.parse_args()
    args.progdir, args.prog = os.path.split(sys.argv[0])
    if args.template: # template can be specified by name or file path
        args.dirname, args.pathname = os.path.split(args.template)
        args.template = args.pathname.split(".yaml")[0]

    if args.subparser_name:
        locals()[args.subparser_name](args)
