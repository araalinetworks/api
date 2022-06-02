#!/usr/bin/env python
"""
    Usage:
        ./setup.sh
        ./template.py pull -t control |less
        ./template.py pull -p -t agent.k8s.araali-fw|less
        ./template.py rename ../templates/control.yaml.1
"""
import araalictl
import argparse
import difflib
import glob
import os
import yaml

class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True

cfg_fname = os.environ['HOME']+"/.araali_templates.cfg"

def read_config():
    if os.path.isfile(cfg_fname):
        with open(cfg_fname, "r") as f:
            cfg = yaml.load(f, Loader=yaml.SafeLoader)
            if not cfg["tenant"]: cfg["tenant"] = None
            return cfg
    return {"tenant": None}

def config(args):
    cfg = read_config()
    if args.tenant is not None:
        if not args.tenant:
            args.tenant = None
        cfg["tenant"] = args.tenant
        with open(cfg_fname, "w") as f:
            yaml.dump(cfg, f)
    
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
        basename = "../templates/%s.yaml" % self.name
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
        key_order = ["name", "dns_pattern", "dst_port",
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

def pull(args):
    cfg = read_config()
    for obj in araalictl.fetch_templates(public=args.public, tenant=cfg["tenant"],
                                       template=args.template):
        # keys: ['name', 'template', 'use', 'author', 'version']
        graph = Graph(args.template)
        for link in obj["template"]:
            #print(yaml.dump(link))

            link_filter = link["link_filter"]

            client = NodeWithPushdown(Node(link_filter["client"], None),
                        Node(link.get("selector_change", {}).get("client", {})))
            server = NodeWithPushdown(Node(link_filter["server"], None),
                        Node(link.get("selector_change", {}).get("server", {})))

            graph.add_link(client, server)

        graph.dump()

def rename(args):
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
    parser = argparse.ArgumentParser(description = 'Manage Templates as Code')
    parser.add_argument('--verbose', '-v', action='count', default=0)
    subparsers = parser.add_subparsers(dest="subparser_name")
    
    parser_pull = subparsers.add_parser("pull", help="pull araali templates")
    parser_pull.add_argument('-p', '--public', action="store_true")
    parser_pull.add_argument('-t', '--template', help="pull a specific template (name or path)")
    
    parser_config = subparsers.add_parser("config", help="add config params")
    parser_config.add_argument('-t', '--tenant')

    parser_rename = subparsers.add_parser("rename", help="rename template node name")
    parser_rename.add_argument('template')

    yaml.add_representer(Node, represent_node)
    yaml.add_representer(NodeWithPushdown, represent_node_with_pushdown)
    yaml.add_representer(Graph, represent_graph)
    yaml.add_representer(NameWithInOut, represent_name_with_in_out)

    args = parser.parse_args()
    if args.template: # template can be specified by name or file path
        args.dirname, args.pathname = os.path.split(args.template)
        args.template = args.pathname.split(".yaml")[0]

    if args.subparser_name:
        locals()[args.subparser_name](args)
