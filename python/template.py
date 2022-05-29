#!/usr/bin/env python
"""
    Usage:
        (araali) python abhishek$ ./template.py list -t control |less
        (araali) python abhishek$ ./template.py list -p -t agent.k8s.araali-fw|less
"""
import araalictl
import argparse
import os
import yaml

cfg_fname = os.environ['HOME']+"/.araali_templates.cfg"

def read_config():
    if os.path.isfile(cfg_fname):
        with open(cfg_fname, "r") as f:
            cfg = yaml.load(f, Loader=yaml.SafeLoader)
            if not cfg["tenant"]: cfg["tenant"] = None
            return cfg
    return {}

def config(args):
    cfg = read_config()
    if args.tenant is not None:
        if not args.tenant:
            args.tenant = None
        cfg["tenant"] = args.tenant
        with open(cfg_fname, "w") as f:
            yaml.dump(cfg, f)
    
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
    def __init__(self, obj):
        self.obj = obj

def represent_node(dumper, obj):
    def rank(key):
        key = key[0].value
        key_order = ["dns_pattern", "dst_port", "zone", "app", "pod", "container", "binary_name", "parent_process", "process"]
        key_order = dict(zip(key_order, range(0, len(key_order))))
        return key_order[key]

    value = []
    for item_key, item_value in obj.obj.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    value.sort(key=lambda x: rank(x))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

def list(args):
    cfg = read_config()
    node_dict = {}
    for obj in araalictl.fetch_templates(public=args.public, tenant=cfg["tenant"],
                                       template=args.template):
        # keys: ['name', 'template', 'use', 'author', 'version']
        ret = []
        for link in obj["template"]:
            #print(yaml.dump(link))

            link_filter = link["link_filter"]

            client = NodeWithPushdown(Node(link_filter["client"]), Node(link.get("selector_change", {}).get("client", {})))
            server = NodeWithPushdown(Node(link_filter["server"]), Node(link.get("selector_change", {}).get("server", {})))

            client_key = yaml.dump(client)
            server_key = yaml.dump(server)
            
            node_dict.setdefault(client_key, client)
            node_dict.setdefault(server_key, server)

            #print(yaml.dump(server))

        i = 0
        items = [a for a in node_dict.items()]
        # XXX: need to sort consistently and properly, so similar nodes show up together
        # and are easy to review
        #items.sort(key=lambda x: x[0])
        for k,v in items:
            print("==== %s ====" % i)
            print(yaml.dump(v))
            i += 1
        return ret

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Manage templates as Code')
    subparsers = parser.add_subparsers(dest="subparser_name")
    
    parser_list = subparsers.add_parser("list", help="list araali templates")
    parser_list.add_argument('-p', '--public', action="store_true")
    parser_list.add_argument('-t', '--template')
    
    parser_config = subparsers.add_parser("config", help="add config params")
    parser_config.add_argument('--tenant')

    yaml.add_representer(Node, represent_node)
    yaml.add_representer(NodeWithPushdown, represent_node_with_pushdown)

    args = parser.parse_args()
    if args.subparser_name:
        locals()[args.subparser_name](args)
