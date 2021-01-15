import json
import re

import araalictl


class Process(object):
    def __init__(self, data):
        self.from_yaml(data)

    def from_yaml(self, data):
        self.zone = data["zone"]
        self.app = data["app"]
        self.process = data["process"]
        self.binary_name = data["binaryname"]
        self.parent_process = data["parentprocess"]

    def __repr__(self):
        return json.dumps(self.to_data())

    def to_data(self):
        if self.zone:
            obj = {"zone": self.zone, "app": self.app, "process": self.process,
                    "parent_process": self.parent_process, "binary_name": self.binary_name}
            for attr in dir(self):
                if "orig_" == attr[:len("orig_")]:
                    obj[attr] = getattr(self, attr)
            return obj
        else:
            return {}

    def change(self, what, to):
        orig_str = "orig_%s" % what
        if not hasattr(self, orig_str):
            setattr(self, orig_str, getattr(self, what))
        setattr(self, what, to)
        return self

    def restore(self, what):
        orig_str = "orig_%s" % what
        setattr(self, what, getattr(self, orig_str))
        return self

    def to_policy(self, client=False, araali=False):
        def set_selectors(app_selector):
            app_selector.selectors["zone"].regex.reg_ex_str = "^%s$" % self.zone
            app_selector.selectors["app"].regex.reg_ex_str = ".*:%s:.*" % self.app
            app_selector.selectors["displayProcess"].regex.reg_ex_str = "^%s$" % self.process
            app_selector.selectors["binaryName"].regex.reg_ex_str = "^%s$" % self.binary_name
            app_selector.selectors["parentProcessName"].regex.reg_ex_str = "^%s$" % self.parent_process
            app_selector.label = "%s--%s--%s--%s" % (self.zone, self.app, self.parent_process, self.process)
        if client: # Always for araali to araali policy need to create araali policy
            policy = policy_pb2.ServicePolicy()
            set_selectors(policy.whitelist_match)
            return policy
        else:
            policy = policy_pb2.AppCtxAwarePolicy() if araali else policy_pb2.NonAraaliPolicies()
            set_selectors(policy.app_selector)
            return policy

    def to_lib(self, zone, app):
        self.zone = zone
        self.app = app


class NonAraaliClient(object):
    def __init__(self, data):
        self.process = None
        self.from_yaml(data)

    def from_yaml(self, data):
        self.subnet = data["subnet"]
        self.net_mask = data["netmask"]

    def __repr__(self):
        return json.dumps(self.to_data())

    def to_data(self):
        return {"network": str(self.subnet), "mask": self.net_mask}

    def to_policy(self):
        nap = policy_pb2.NonAraaliServicePolicy()
        nap.addr_mask.ip_addr.v6_addr = self.subnet.packed
        nap.addr_mask.mask_len = self.net_mask
        nap.low_port = 0
        nap.high_port = (1 << 16) - 1
        nap.label = "%s/%s" % (str(self.subnet), self.net_mask)
        return nap

    def to_lib(self, zone, app):
        pass


class NonAraaliServer(object):
    def __init__(self, data):
        self.process = None
        self.from_yaml(data)

    def from_yaml(self, data):
        self.dst_port = data["dstport"]
        if "dnsPattern" in data:
            self.dns_pattern = data["dnsPattern"]
        else:
            self.dns_pattern = None
            self.subnet = data["subnet"]
            self.net_mask = data["netmask"]

    def __repr__(self):
        return json.dumps(self.to_data())

    def change(self, what, to):
        orig_str = "orig_%s" % what
        if not hasattr(self, orig_str):
            setattr(self, orig_str, getattr(self, what))
        setattr(self, what, to)
        return self

    def restore(self, what):
        orig_str = "orig_%s" % what
        setattr(self, what, getattr(self, orig_str))
        return self

    def to_data(self):
        if self.dns_pattern:
            obj = {"dns_pattern": self.dns_pattern, "dst_port": self.dst_port}
        else:
            obj = {"network": str(self.subnet), "mask": self.net_mask, "dst_port": self.dst_port}

        for attr in dir(self):
            if "orig_" == attr[:len("orig_")]:
                obj[attr] = getattr(self, attr)
        return obj

    def to_policy(self):
        nap = policy_pb2.NonAraaliServicePolicy()
        if self.dns_pattern:
            #nap.dns_pattern = re.sub(":", "|", self.dns_pattern)
            label = self.dns_pattern
        else:
            nap.addr_mask.ip_addr.v6_addr = self.subnet.packed
            nap.addr_mask.mask_len = self.net_mask
            label = "%s/%s" % (str(self.subnet), self.net_mask)
        nap.low_port = self.dst_port
        nap.high_port = self.dst_port if self.dst_port != 0 else (1 << 16) - 1
        nap.label = "%s:%s" % (label, nap.low_port if nap.low_port == nap.high_port else "[%s-%s]" % (nap.low_port, nap.high_port))
        return nap

    def to_lib(self, zone, app):
        pass


class AcceptLink:                                                               
    def __init__(self, filters, changes=[]):                                    
        self.filters = filters                                                  
        self.changes = changes                                                  
                                                                                
    def apply(self, links):                                                     
        l = LinkTable(links, f.lstate("BASELINE_ALERT"), f.nstate(None), *self.filters)                                     
        l.accept()                                                              
        for c in self.changes:                                                       
            l.change(*c)
        return l.links


class MetaPolicyRunner:
    def __init__(self, *args):
        self.args = []
        for a in args:
            self.args.append(a)

    def add(self, *args):
        for a in args:
            self.args.append(a)

    def run(self, links):
        self.links = links
        for meta_policy in self.args:
            pname = meta_policy.__name__
            count = 0
            for policy in meta_policy.policies:
                for l in policy.apply(self.links):
                    l.meta_policy = pname
                    count += 1
            print("%-20s matched %s rows" % (pname, count))
        return self

    def review(self):
        def impl():
            for l in self.links:
                if l.new_state == None:
                    continue
                obj = l.to_data()
                obj["meta_policy"] = l.meta_policy
                yield obj
        ret = list(impl())
        print("\nReviewing %s rows" % len(ret))
        return Table(ret)
    

class Table(object):
    def check_notebook():
        try:
            return get_ipython().has_trait('kernel')
        except:
            return False

    in_notebook = check_notebook()

    def transform(a):
        op = getattr(a, "to_data", None)
        if callable(op):
            return a.to_data()
        else:
            return a

    def __init__(self, links, *filters):
        def eval_filters(a):
            for filter in filters:
                if not filter(a):
                    return False
            return True

        self.links = [a for a in links if eval_filters(Table.transform(a))]

    def to_data(self):
        return [Table.transform(a) for a in self.links]

    def to_yaml(self, *args):
        if not args:
            args = range(len(self.links))
        data = self.to_data()
        for i in args:
            print("%s %s %s" % ("-"*40, i, "-"*40))
            print(yaml.dump(data[i]))
        return self

    def _repr_html_(self):
        return display(pd.DataFrame(self.to_data()))

    def __repr__(self):
        if Table.in_notebook:
            return ""
        return json.dumps(self.to_data())


class LinkTable(Table):
    class Filter:
        def all(r):
            return True

        def neg(filter):
            return lambda r: not filter(r)

        def lstate(state):
            """Valid states are: NAI, NAE, INT, AIN, AEG"""
            return lambda r: r.get("lstate", None) == state

        def ltype(link_type):
            return lambda r: r.get("ltype", None) == link_type

        def nstate(state):
            return lambda r: r.get("nstate", None) == state

        def speculative(state):
            return lambda r: r.get("speculative", None) == state

        def endpoint(field, val, flags=0, who="either"):
            """flags=re.IGNORECASE can be used"""
            # examples:
            #   f.endpoint("dns_pattern", "api.snapcraft.io"),
            #   f.endpoint("network", "169.254.169.254", who="server")
            #   f.neg(f.endpoint("process", ansible", re.IGNORECASE)),
            #   f.endpoint("binary_name", "/snap/amazon-ssm-agent"), #/2996/ssm-agent-worker")
            #   f.endpoint("process", "sshd", re.IGNORECASE),
            #   f.endpoint("process", ["sshd", "haproxy"], who="server"),
            #   f.endpoint("network", None, who="server"), # perimeter
            #   f.neg(f.endpoint("network", None, who="server")), # perimeter

            def match_str(s, v):
                return re.search(s, v, flags=flags)

            def match_nonstr(s, v):
                if isinstance(s, list):
                    return v in s
                return s == v

            match_val = match_str if isinstance(val, str) else match_nonstr

            def match(r):
                c = r.get("client", {}).get(field, "" if isinstance(val, str) else None)
                s = r.get("server", {}).get(field, "" if isinstance(val, str) else None)
                if who == "client":
                    return match_val(val, c)
                elif who == "server":
                    return match_val(val, s)
                else: # match either
                    return match_val(val, c) or match_val(val, s)
                return  False
            return match

        def perimeter(r):
            return r.get("client", {}).get("network", None) != None

        def server_non_ip(r):
            s = r.get("server", {})
            return s.get("dns_pattern", "")[:3] != "ip-" and s.get("network", None) == None

        def same_zone(r):
            return r.get("client", {}).get("zone", None) == r.get("server", {}).get("zone", None)

    def change(self, what, field, to, *args):
        if not args:
            args = range(len(self.links))
        for i in args:
            getattr(self.links[i], what).change(field, to)
        return self

    def restore(self, what, field, *args):
        if not args:
            args = range(len(self.links))
        for i in args:
            getattr(self.links[i], what).restore(field)
        return self

    def accept(self, *args):
        if not args:
            args = range(len(self.links))
        for i in args:
            self.links[i].accept()
        return self

    def snooze(self, *args):
        if not args:
            args = range(len(self.links))
        for i in args:
            self.links[i].snooze()
        return self


f = LinkTable.Filter
class MpNAE:                                                                 
    policies = [
        AcceptLink(filters=[
                f.ltype("NAE"),
                f.endpoint("process", "/usr/local/bin/cvescan", who="client"),
                f.endpoint("dns_pattern", "people.canonical.com", who="server"),
            ], changes=[
                ("server", "dns_pattern", ":people\.canonical\.com:"),
            ]),
        AcceptLink(filters=[                                                    
                f.ltype("NAE"),                                                 
                f.endpoint("process", "dockerd", who="client"),                 
                f.endpoint("dns_pattern", [
                    "175118736976.dkr.ecr.us-west-2.amazonaws.com",
                ], who="server"),           
            ], changes=[                                                        
                ("server", "dns_pattern", ":175118736976\.dkr\.ecr\..*\.amazonaws\.com:"),
            ]),        
        AcceptLink(filters=[                                                    
                f.ltype("NAE"),                                                 
                f.endpoint("process", "grafana-server", who="client"),                 
                f.endpoint("dns_pattern", [
                    "hooks.slack.com", 
                    "grafana.com",
                    "raw.githubusercontent.com",
                ], who="server"),           
            ], changes=[                                                        
            ]),
        AcceptLink(filters=[                                                    
                f.ltype("NAE"),                                                 
                f.endpoint("process", "kubelet", who="client"),                 
                f.endpoint("dns_pattern", [
                    "ec2.us-west-2.amazonaws.com", 
                    "api.ecr.us-west-2.amazonaws.com",
                ], who="server"),           
            ], changes=[                                                        
            ]),         
        AcceptLink(filters=[                                                    
                f.ltype("NAE"),                                                 
                f.endpoint("process", "kubelet", who="client"),                 
                f.endpoint("dns_pattern", ".*.eks.amazonaws.com", who="server"),           
            ], changes=[                                                        
                ("server", "dns_pattern", ":.*\.eks\.amazonaws\.com:"),
            ]),        
        AcceptLink(filters=[                                                    
                f.endpoint("app", "cassandra"),                           
                f.ltype("NAE"),                                                 
                f.endpoint("process", "/usr/bin/pip3", who="client"),               
                f.endpoint("dns_pattern", ["pypi.python.org",
                                           "pypi.org",
                                           "files.pythonhosted.org"], who="server"),           
            ], changes=[                                                        
            ]),                                                                 
        AcceptLink(filters=[                                                    
                f.ltype("NAE"),                                                 
                f.endpoint("process", "/usr/lib/ubuntu-release-upgrader/check-new-release", who="client"),                 
                f.endpoint("dns_pattern", ["changelogs.ubuntu.com"], who="server"),           
            ], changes=[                                                        
                ("server", "dns_pattern", ":changelogs\.ubuntu\.com:"),
            ]),
        AcceptLink(filters=[                                                    
                f.ltype("NAE"),                                                 
                f.endpoint("parent_process", "apt-get", who="client"),                 
                f.endpoint("dns_pattern", ["us-west-2.ec2.archive.ubuntu.com",
                                           "downloads.apache.org", 
                                           "www.apache.org",
                                           "security.ubuntu.com",
                                           "dl.bintray.com"], who="server"),           
            ], changes=[                                                        
            ]),         
    ]  

class MpINT:
    policies = [
        AcceptLink(filters=[
                f.ltype("INT"),                                                 
                f.endpoint("process", "grafana-server", who="client"),                 
                f.endpoint("process", "prometheus", who="server"),           
            ], changes=[                                                        
            ]),   
        AcceptLink(filters=[
                f.ltype("INT"),                                                 
                f.endpoint("process", "kube-rbac-proxy", who="client"),                 
                f.endpoint("process", [
                    "node_exporter",
                    "kube-state-metrics"
                ], who="server"),           
            ], changes=[                                                        
            ]),   
        AcceptLink(filters=[
                f.ltype("INT"),                                                 
                f.endpoint("process", "coredns", who="client"),                 
                f.endpoint("process", "coredns", who="server"),           
            ], changes=[                                                        
            ]),   
        AcceptLink(filters=[
                f.ltype("INT"),                                                 
                f.endpoint("process", "kubelet", who="client"),                 
                f.endpoint("process", "kubelet", who="server"),           
            ], changes=[                                                        
            ]),   
    ]

class MpBendVm:
    policies = [
        AcceptLink(filters=[
                f.ltype("INT"),
                f.endpoint("process", "com.araalinetworks.LaunchKt", who="client"),
                f.endpoint("process", "scanner.py", who="server"),
            ], changes=[
            ]),
        AcceptLink(filters=[
                f.endpoint("app", "bendvm.bend.web"),
                f.ltype("NAE"),
                f.endpoint("process", "araaliweb", who="client"),
                f.endpoint("dns_pattern", "ipinfo.io", who="server"),
            ], changes=[
                ("server", "dns_pattern", ":ipinfo\.io:"),
            ]),
        AcceptLink(filters=[
                f.endpoint("app", "bendvm.bend.visbot"),
                f.ltype("NAE"),
                f.endpoint("process", "main.py", who="client"),
                f.endpoint("dns_pattern", "slack.com", who="server"),
            ], changes=[
                ("server", "dns_pattern", ":slack\.com:"),
            ]),
        AcceptLink(filters=[
                f.endpoint("app", "bendvm"),                        
                f.ltype("INT"),                                                 
                f.endpoint("process", "docker-proxy", who="client"),                 
                f.endpoint("process", "main.py", who="server"),           
            ], changes=[                                                        
            ]),   
        AcceptLink(filters=[
                f.endpoint("app", "bendvm.bend.uiserver"),                        
                f.ltype("INT"),                                                 
                f.endpoint("parent_process", "check_health.sh", who="client"),                 
                f.endpoint("process", "grpcwebproxy", who="server"),           
            ], changes=[                                                        
            ]),   
        AcceptLink(filters=[                                                    
                f.endpoint("app", "bendvm.bend.backend"),                        
                f.ltype("INT"),                                                 
                f.endpoint("process", "prometheus", who="client"),                 
                f.endpoint("process", "araali_backend.py", who="server"),           
            ], changes=[                                                        
            ]),         
        AcceptLink(filters=[
                f.same_zone,
                f.ltype("AEG"),                                                 
                f.endpoint("app", "dmzvm", who="client"),                        
                f.endpoint("process", "/var/lib/haproxy/healthcheck.py", who="client"), 
                f.endpoint("app", "bendvm.bend.backend", who="server"),                        
                f.endpoint("process", "prometheus", who="server"),           
            ], changes=[                                                        
            ]),         
        AcceptLink(filters=[
                f.same_zone,
                f.ltype("AEG"),                                                 
                f.endpoint("app", "bendvm.bend.uiserver", who="client"),                        
                f.endpoint("process", "com.araalinetworks.uiserver.UiServerKt", who="client"), 
                f.endpoint("app", "dmzvm", who="server"),                        
                f.endpoint("process", "haproxy", who="server"),           
            ], changes=[                                                        
            ]),        
        AcceptLink(filters=[
                f.same_zone,
                f.ltype("AEG"),                                                 
                f.endpoint("app", "dmzvm", who="client"),                        
                f.endpoint("process", "haproxy", who="client"), 
                f.endpoint("app", "bendvm.bend.web", who="server"),                        
                f.endpoint("process", "araaliweb", who="server"),           
            ], changes=[                                                        
            ]),         
        AcceptLink(filters=[
                f.same_zone,
                f.ltype("AEG"),                                                 
                f.endpoint("app", "dmzvm", who="client"),                        
                f.endpoint("process", "haproxy", who="client"), 
                f.endpoint("app", "bendvm.bend.uiserver", who="server"),                        
                f.endpoint("process", "grpcwebproxy", who="server"),           
            ], changes=[                                                        
            ]),        
        AcceptLink(filters=[
                f.same_zone,
                f.ltype("AEG"),                                                 
                f.endpoint("app", "dmzvm", who="client"),                        
                f.endpoint("process", "haproxy", who="client"), 
                f.endpoint("app", "bendvm.bend.backend", who="server"),                        
                f.endpoint("process", "araali_backend.py", who="server"),           
            ], changes=[                                                        
            ]),           
    ]

class MpSSMagentToMeta:
    policies = [
        AcceptLink(filters=[                                               
                f.endpoint("binary_name", "/snap/amazon-ssm-agent/.*/ssm-agent-worker", who="client"),
                f.endpoint("network", "169.254.169.254", who="server"),
            ], changes=[
                ("client", "binary_name", "/snap/amazon-ssm-agent/[0-9]+/ssm-agent-worker"),
            ]),
    ]

class MpToMetadataSvc:
    policies = [
        AcceptLink(filters=[                                               
                f.endpoint("process", ["kubelet",
                                        "aws-iam-authenticator",
                                        "aws-k8s-agent",
                                        "/usr/bin/yum"], who="client", flags=re.IGNORECASE),
                f.endpoint("network", "169.254.169.254", who="server"),
            ], changes=[
            ]),
    ]

class MpSSMagentToSSM:
    policies = [
        AcceptLink(filters=[                                               
                f.endpoint("binary_name", "/snap/amazon-ssm-agent/.*/ssm-agent-worker", who="client"),
                f.endpoint("dns_pattern", "ssm.us-west-2.amazonaws.com", who="server"),
            ], changes=[
                ("client", "binary_name", "/snap/amazon-ssm-agent/[0-9]+/ssm-agent-worker"),
                ("server", "dns_pattern", ":ssm\..*\.amazonaws\.com:"),
            ]),
    ]

class MpCassandra:
    policies = [
        AcceptLink(filters=[                                                    
                f.endpoint("app", "cassandra"),                      
                f.ltype("INT"),                                                 
                f.endpoint("process", "org.apache.cassandra.tools.NodeTool", who="client"),  
                f.endpoint("process", "org.apache.cassandra.service.CassandraDaemon", who="server"),            
            ], changes=[                                                        
            ]), 
        AcceptLink(filters=[                                                    
                f.endpoint("app", "cassandra"),                      
                f.ltype("INT"),                                                 
                f.endpoint("process", "curl", who="client"),  
                f.endpoint("process", "cassandra_monitoring.py", who="server"),            
            ], changes=[                                                        
            ]), 
        AcceptLink(filters=[                                               
                f.endpoint("process", ["com.araalinetworks.LaunchKt", 
                                       "com.araalinetworks.uiserver.UiServerKt",
                                       "/usr/bin/cqlsh.py", 
                                       "sshd"
                                      ], who="client", flags=re.IGNORECASE),
                f.endpoint("process", "cassandra", who="server", flags=re.IGNORECASE),
            ], changes=[
            ]),
    ]

class MpDynamo:
    policies = [
        AcceptLink(filters=[                                               
                f.endpoint("process", ["araali_backend.py", 
                                       "com.araalinetworks.uiserver.UiServerKt",
                                       "com.araalinetworks.LaunchKt",
                                       "araaliweb",
                                      ], who="client", flags=re.IGNORECASE),
                f.endpoint("dns_pattern", "dynamodb..*.amazonaws.com"),
            ], changes=[
                ("server", "dns_pattern", ":dynamodb\..*\.amazonaws\.com:"),
            ]),
    ]

class MpS3:
    policies = [
        AcceptLink(filters=[                                               
                f.endpoint("process", ["service_processor.py", 
                                       "com.araalinetworks.uiserver.UiServerKt",
                                       "com.araalinetworks.LaunchKt",
                                       "/usr/local/bin/aws",
                                      ], who="client", flags=re.IGNORECASE),
                f.endpoint("dns_pattern", "s3\..*\.amazonaws\.com"),
            ], changes=[
                ("server", "dns_pattern", ":s3\..*\.amazonaws\.com:"),
            ]),
    ]

class MpGtor:
    policies = [
        AcceptLink(filters=[                                               
                f.endpoint("process", ["autok8s", "guarantor"], who="client", flags=re.IGNORECASE),
                f.endpoint("dns_pattern", ".*.fog.aws.araalinetworks.com"),
            ], changes=[
                ("server", "dns_pattern", ":.*\.fog\.aws\.araalinetworks\.com:"),
            ]),
    ]

class MpSnapdToSnapcraft:
    policies = [
        AcceptLink(filters=[                                               
                f.endpoint("binary_name", "/snap/core/[0-9]+/usr/lib/snapd/snapd", who="client"),
                f.endpoint("dns_pattern", "api.snapcraft.io"),
            ], changes=[
                ("client", "binary_name", "/snap/core/[0-9]+/usr/lib/snapd/snapd"),
                ("server", "dns_pattern", ":api\.snapcraft\.io:"),
            ]),
    ]

class MpMotd:
    policies = [
        AcceptLink(filters=[                                               
                f.endpoint("parent_process", "50-motd-news", who="client"),
                f.endpoint("dns_pattern", "motd.ubuntu.com"),
            ], changes=[
                ("server", "dns_pattern", ":motd\.ubuntu\.com:"),
            ]),
    ]

class MpAwsK8sAgent:
    policies = [
        AcceptLink(filters=[                                               
                f.endpoint("process", "aws-k8s-agent", flags=re.IGNORECASE, who="client"),
                f.endpoint("dns_pattern", "ec2.us-west-2.amazonaws.com"),
            ], changes=[
                ("server", "dns_pattern", ":ec2\..*\.amazonaws\.com:"),
            ]),
    ]
    
class MpPerimeter:
    policies = [
        AcceptLink(filters=[                                               
                f.perimeter,
                f.endpoint("process", ["sshd", "haproxy"], who="server", flags=re.IGNORECASE),
            ], changes=[
            ]),
    ]
    
class MpGrpcHealthProbe:                                                              
    policies = [
        AcceptLink(filters=[                                               
                f.same_zone,
                f.endpoint("process", "grpc-health-probe", who="client", flags=re.IGNORECASE),
                f.endpoint("process", "aws-k8s-agent", who="server", flags=re.IGNORECASE),
            ], changes=[
            ]),
    ]
                                                                                
class MpAmznLinux:                                                              
    policies = [
        AcceptLink(filters=[                                               
                f.endpoint("process", ["/usr/bin/yum", "amazon_linux_extras"], who="client", flags=re.IGNORECASE),
                f.endpoint("dns_pattern", "amazonlinux.us-west-2.amazonaws.com", who="server", flags=re.IGNORECASE),
            ], changes=[
                ("server", "dns_pattern", ":amazonlinux\..*\.amazonaws\.com:"),
            ]),
    ]

class MpCheckHealth:                                                              
    policies = [
        AcceptLink(filters=[                                               
                f.same_zone,
                f.endpoint("parent_process", "check_health.sh", who="client"),
                f.endpoint("process", "grpcwebproxy", who="server", flags=re.IGNORECASE),
            ], changes=[
            ]),
    ]

class MpHbCheck:
    policies = [
        AcceptLink(filters=[                                               
                f.endpoint("binary_name", "/snap/amazon-ssm-agent/.*/ssm-agent-worker", who="client"),
                f.endpoint("network", "169.254.169.254", who="server"),
            ], changes=[
                ("client", "binary_name", "/snap/amazon-ssm-agent/[0-9]+/ssm-agent-worker"),
            ]),
    ]

    policies = [
        AcceptLink(filters=[                                               
                f.ltype("INT"),
                f.endpoint("process", "heartbeat_check.py", who="client"),
                f.endpoint("process", "com.araalinetworks.LaunchKt", who="server", flags=re.IGNORECASE),
            ], changes=[
            ]),
    ]

class MpHealthCheck:
    policies = [
        AcceptLink(filters=[                                               
                f.same_zone,
                f.endpoint("process", "/var/lib/haproxy/healthcheck.py", who="client"),
                f.endpoint("process", "prometheus", who="server", flags=re.IGNORECASE),
            ], changes=[
            ]),
    ]

class MpHaproxyClient:
    policies = [
        AcceptLink(filters=[                                               
                f.same_zone,
                f.endpoint("process", "haproxy", who="client"),
                f.endpoint("process", ['araali_backend.py', "grpcwebproxy", "araaliweb"], who="server", flags=re.IGNORECASE),
            ], changes=[
            ]),
    ]

class MpHaproxyServer:
    policies = [
        AcceptLink(filters=[                                               
                f.same_zone,
                f.endpoint("process", ["com.araalinetworks.uiserver.UiServerKt", "araali_health_check.py"], who="client"),
                f.endpoint("process", "haproxy", who="server", flags=re.IGNORECASE),
            ], changes=[
            ]),
    ]

class MpPrometheus:
    policies = [
        AcceptLink(filters=[                                               
                f.same_zone,
                f.endpoint("process", "prometheus", who="client"),
                f.endpoint("process", ["araali_backend.py", "node_exporter", "prometheus", "kubelet", "kube-rbac-proxy", "com.araalinetworks.LaunchKt"], who="server", flags=re.IGNORECASE),
            ], changes=[
            ]),
    ]

class MpAlertMgr:
    policies = [
        AcceptLink(filters=[                                               
                f.ltype("INT"),
                f.endpoint("process", "alertmanager", who="client"),
                f.endpoint("process", "alertmanager", who="server", flags=re.IGNORECASE),
            ], changes=[
            ]),
    ]

class MpKubeletClient:
    policies = [
        AcceptLink(filters=[                                               
                f.same_zone,                     
                f.endpoint("process", "kubelet", who="client"),
                f.endpoint("process", ["grafana-server", "prometheus"], who="server", flags=re.IGNORECASE),
            ], changes=[
            ]),
    ]


mpr = MetaPolicyRunner()
mpr.add(
        MpBendVm, MpNAE, MpINT,
        MpSSMagentToMeta,
        MpToMetadataSvc, MpSSMagentToSSM, MpCassandra, MpDynamo, MpS3, MpGtor,
        MpSnapdToSnapcraft, MpMotd, MpAwsK8sAgent, MpPerimeter, MpGrpcHealthProbe,
        MpAmznLinux, MpCheckHealth, MpHbCheck, MpHealthCheck, MpHaproxyClient,
        MpHaproxyServer, MpPrometheus, MpAlertMgr,
        MpKubeletClient,
)


class Link(object):
    def __init__(self, data, zone, app):
        self.client = Process(data["client"]) if "client" in data else NonAraaliClient(data["nonAraaliClient"])
        self.server = Process(data["server"]) if "server" in data else NonAraaliServer(data["nonAraaliServer"])
        self.ltype = data["type"]
        self.speculative = data["speculative"]
        self.lstate = data["state"]
        self.timestamp = data["timestamp"]
        self.unique_id = data["uniqueid"]
        self.new_state = None

    def to_data(self):
        return {"client": self.client.to_data(), "server": self.server.to_data(),
                "ltype": self.ltype, "lstate": self.lstate,
                "nstate": self.new_state, "speculative": self.speculative}

    def accept(self):
        self.new_state = "DEFINED_POLICY"

    def snooze(self):
        self.new_state = "snooze"

    def to_alert_info(self, alert_status):
        alert_request = araali_ui_pb2.ManageAlertsRequest()
        alert_request.tenant_id = 'meta-tap' # Fix me
        alert_request.email = 'abhishek@araalinetworks.com'
        alert_info = alert_request.alert_and_status.add()
        alert_info.alert_id = self.unique_id
        alert_info.status = alert_status
        alert_info.timestamp = self.timestamp
        if self.ltype == "AEG" or self.ltype == "NAE":
            zone = self.client.zone
            app = self.client.outer
        else:
            zone = self.server.zone
            app = self.server.outer
        alert_info.zone = zone
        alert_info.app = app
        return alert_request

    def to_request(self):
        policy_request = araali_ui_pb2.PolicyRequest()
        if self.new_state == "DEFINED_POLICY":
            policy_request.op = araali_ui_pb2.PolicyRequest.Op.ADD
            if self.lstate == "BASELINE_ALERT":
                policy_request.alert_request.CopyFrom(self.to_alert_info(flow_spec_pb2.AlertType.AlertStatus.CLOSE))

        elif self.new_state == "snooze":
            if self.lstate == "BASELINE_ALERT":
                return self.to_alert_info(flow_spec_pb2.AlertType.AlertStatus.CLOSE)
            policy_request.op = araali_ui_pb2.PolicyRequest.Op.DEL
        else:
            return None

        if self.ltype == "NAI":
            policy_request.policy.non_araali_policies.extend([self.server.to_policy()])
            policy_request.policy.non_araali_policies[0].ingress_policies.extend([self.client.to_policy()])
            policy_request.policy.non_araali_policies[0].rank = 5000
        elif self.ltype == "NAE":
            policy_request.policy.non_araali_policies.extend([self.client.to_policy()])
            policy_request.policy.non_araali_policies[0].egress_policies.extend([self.server.to_policy()])
            policy_request.policy.non_araali_policies[0].rank = 5000
        else: # We always create ingress policies in case of araali to araali.
            policy_request.policy.app_ctx_policies.extend([self.server.to_policy(client=False, araali=True)])
            policy_request.policy.app_ctx_policies[0].ingress_policies.extend([self.client.to_policy(client=True, araali=True)])
            policy_request.policy.app_ctx_policies[0].rank = 5000
        return policy_request

    def to_lib(self, zone, app):
        if self.ltype == "INT":
            self.client.to_lib(zone, app)
            self.server.to_lib(zone, app)
        elif self.ltype == "NAE" or self.ltype == "AEG":
            self.client.to_lib(zone, app)
        else: # NAI or AIN
            self.server.to_lib(zone, app)

    def __repr__(self):
        return json.dumps(self.to_data())


class Runtime(object):
    zones = ["dev", "ops", "prod", "nightly", "prod-k8s", "nightly-k8s"]
    def __init__(self):
        self.zones = None

    def refresh(self):
        if self.zones == None:
            self.zones = [Zone(z) for z in Runtime.zones]
            return self

        for z in self.zones:
            z.refresh()
        return self

    def iterzones(self, filter=None):
        def impl():
            for z in self.zones:
                if filter and z.zone != filter:
                    continue
                yield z

        res = impl()
        if filter:
            return list(res)[0]
        else:
            return list(res)
        
    def stats(self, all=False):
        def impl():
            for z in self.zones:
                for s in z.stats(all):
                    s["Zone"] = z.zone
                    yield s
        return list(impl())

    def review(self, data=False):
        for z in self.iterzones():
            for l in z.review(data):
                yield l

    def commit(self):
        def impl():
            for z in self.iterzones():
                for c in z.commit():
                    obj = c
                    obj["Zone"] = z.zone
                    yield obj
        return list(impl())

    def accept(self):
        for a in self.iterzones():
            a.accept()
        return self
 
    def snooze(self):
        for a in self.iterzones():
            a.snooze()
        return self
 
    def iterlinks(self, lfilter=None, pfilter=None, cfilter=False, afilter=False, dfilter=False, data=False):
        for z in self.iterzones():
            for link in z.iterlinks(lfilter, pfilter, cfilter, afilter, dfilter, data):
                yield link

    def to_data(self):
        return [z.to_data() for z in self.iterzones()]

    def __repr__(self):
        return json.dumps(self.to_data())


class Zone(object):
    zone2apps = {
        "dev": ["cassandra"],
        "ops": ["cassandra"],
        "prod": ["dmzvm", "bendvm"],
        "nightly": ["dmzvm", "bendvm"],
        "prod-k8s": ["k8s", "kube-system", "monitoring", "prod-araali-operator", "prod-bend"],
        "nightly-k8s": ["k8s", "kube-system", "monitoring", "prod-araali-operator", "prod-bend"],
    }

    def __init__(self, name):
        self.zone = name
        self.apps = [App(name, a) for a in Zone.zone2apps[name]]

    def refresh(self):
        for a in self.apps:
            a.refresh()
        return self

    def iterapps(self, filter=None):
        def impl():
            for a in self.apps:
                if filter and a.app != filter:
                    continue
                yield a

        res = impl()
        if filter:
            return list(res)[0]
        else:
            return list(res)
 
    def stats(self, all=False):
        def impl():
            for a in self.apps:
                for s in a.stats(all):
                    s["App"] = a.app
                    yield s
        return list(impl())

    def iterlinks(self, lfilter=None, pfilter=None, cfilter=False, afilter=False, dfilter=False, data=False):
        for app in self.iterapps():
            for link in app.iterlinks(lfilter, pfilter, cfilter, afilter, dfilter, data):
                yield link

    def review(self, data=False):
        for a in self.iterapps():
            for l in a.review(data):
                yield l

    def commit(self):
        def impl():
            for a in self.iterapps():
                obj = a.commit()
                obj["App"] = a.app
                yield obj
        return list(impl())

    def accept(self):
        for app in self.iterapps():
            app.accept()
        return self
 
    def snooze(self):
        for app in self.iterapps():
            app.snooze()
        return self
 
    def to_data(self):
        return [a.to_data() for a in self.iterapps()]

    def __repr__(self):
        return json.dumps(self.to_data())
            

class App(object):
    ZONE_MARKER = "__ZONE__"
    APP_MARKER = "__APP__"

    def __init__(self, zone, app):
        self.zone = zone
        self.app = app
        self.refresh() # get links

    def refresh(self):
        self.links = []
        for link in araalictl.get_links(self.zone, self.app):
            self.links.append(Link(link, self.zone, self.app))
        return self
        
    def iterlinks(self, lfilter=None, pfilter=None, cfilter=False, afilter=False, dfilter=False, data=False):
        """lfilter for ltype, pfilter for process, cfilter for changes/dirty
           afilter for alerts, dfilter for defined
        """
        def impl():
            for l in self.links:
                if lfilter and l.ltype != lfilter:
                    continue
                # for process filter, it could be either client or server
                proc = []
                if l.client: # araali guy
                    proc.append(l.client)
                if l.server:
                    proc.append(l.server)
                if pfilter and pfilter not in [a.process for a in proc]:
                    continue
                if cfilter and l.new_state is None:
                    continue
                if afilter: # show only alerts
                     if l.lstate != "BASELINE_ALERT" or l.ltype == "NAI" and l.speculative:
                        continue
                if dfilter: # show only defined
                     if l.lstate != "DEFINED_POLICY":
                        continue
                yield l
        if data:
            return [a.to_data() for a in impl()]
        return list(impl())

    def commit(self):
        """accept policy etc backend calls"""
        # iterate thru change filter and push to backend
        policy_request_list = araali_ui_pb2.PolicyRequestList()
        policy_request_list.tenant_id = "meta-tap" # FIXME: Parameterize later
        manage_alerts_request = araali_ui_pb2.ManageAlertsRequest()
        manage_alerts_request.tenant_id = "meta-tap"
        manage_alerts_request.email = "abhishek@araalinetworks.com"
        for link in self.review():
            ui_request = link.to_request()
            if isinstance(ui_request, araali_ui_pb2.PolicyRequest):
                policy_request_list.policy_requests.extend([ui_request])
            elif isinstance(ui_request, araali_ui_pb2.ManageAlertsRequest):
                for a in ui_request.alert_and_status:
                    manage_alerts_request.alert_and_status.extend([a])
            else:
                # Unsupported transition
                pass

        ret_val = {}
        if len(policy_request_list.policy_requests) > 0:
            ret_val['policies'] = araali.backend.push_policies(policy_request_list)
        if len(manage_alerts_request.alert_and_status) > 0:
            ret_val['alerts'] = araali.backend.manage_alerts(manage_alerts_request)
        else:
            ret_val['empty'] = {"success": "Empty policy request"}
        return ret_val

    def review(self, data=False):
        """display any state changes prior to commit, data is set to true if you want data instead of objects"""
        return self.iterlinks(cfilter=True, data=data)

    def accept(self):
        for link in self.iterlinks(afilter=True):
            link.accept()
        return self
 
    def snooze(self):
        for link in self.iterlinks():
            link.snooze()
        return self
        
    def to_data(self):
        return {"zone": self.zone, "app": self.app, "links": [a.to_data() for a in self.links]}

    def stats(self, all=False):
        def impl():
            link_type = {}                                                          
            for link in self.iterlinks():
                if link.lstate == "BASELINE_ALERT" and link.ltype == "NAI" and link.speculative:
                    continue # skip baseline alerts
                link_type.setdefault(link.ltype, {}).setdefault(link.lstate, []).append(1)                      

            for k, sdict in link_type.items():
                for state, v in sdict.items():
                    if not all and state != "BASELINE_ALERT":
                        continue
                    yield {"Type": {"INT": "Internal", 
                                    "NAI": "Non-Araali Ingress",
                                    "NAE": "Non-Araali Egress",
                                    "AIN": "Araali Ingress",
                                    "AEG": "Araali Egress"
                                   }[k], "Link State": state, "Num Links": len(v)}
        return list(impl())

    def relocate(self, zone, app):
        lib_app = self.to_lib()
        lib_app.instantiate(zone, app)
        return lib_app

    def to_lib(self):
        lib_app = copy.deepcopy(self)
        lib_app.zone = self.ZONE_MARKER
        lib_app.app = self.APP_MARKER
        for link in lib_app.iterlinks():
            link.to_lib(self.ZONE_MARKER, self.APP_MARKER)
        return lib_app

    def instantiate(self, zone, app):
        self.zone = zone
        self.app = app
        for link in self.iterlinks():
            if link.lstate == "DEFINED_POLICY":
                link.accept()
            link.to_lib(zone, app)

    def __repr__(self):
        return json.dumps(self.to_data())



