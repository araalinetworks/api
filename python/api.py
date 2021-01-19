import copy
import json
import re

try:
    import pandas as pd
    pd.set_option("display.max_colwidth", 400) # was 50
    pd.set_option("display.max_rows", 1000)
except:
    pass

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
            self.net_mask = data.get("netmask", 0)

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
        self.mp_names = {}
        self.add(*args)

    def add(self, *args):
        for a in args:
            self.mp_names[a.__name__] = a

    def run(self, links):
        self.links = list(links)
        for pname, meta_policy in self.mp_names.items():
            count = 0
            for policy in meta_policy.policies:
                for l in policy.apply(self.links):
                    l.meta_policy = pname
                    count += 1
            print("%-20s matched %s rows" % (pname, count))
        return self

    def review(self, *filters):
        filters = [a.__name__ for a in filters]
        def impl():
            for l in self.links:
                if l.new_state == None:
                    continue
                if filters and l.meta_policy not in filters:
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

        def any(*filters):
            def impl(r):
                for f in filters:
                    if f(r):
                        return True
                return False
            return impl

        def neg(*filters):
            def impl(r):
                for f in filters:
                    if f(r):
                        return False
                return True
            return impl

        def lstate(state):
            """Valid states are: NAI, NAE, INT, AIN, AEG"""
            if isinstance(state, list):
                return lambda r: r.get("lstate", None) in state
            return lambda r: r.get("lstate", None) == state

        def ltype(link_type):
            if isinstance(link_type, list):
                return lambda r: r.get("ltype", None) in link_type
            return lambda r: r.get("ltype", None) == link_type

        def nstate(state):
            if isinstance(state, list):
                return lambda r: r.get("nstate", None) in state
            return lambda r: r.get("nstate", None) == state

        def speculative(state):
            if isinstance(state, list):
                return lambda r: r.get("speculative", None) in state
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

    def meta_policy(self, *args):
        if not args:
            args = range(len(self.links))
        for i in args:
            self.links[i].meta_policy()


f = LinkTable.Filter
mpr = MetaPolicyRunner()

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

    def meta_policy(self):
        if self.ltype == "NAI":
            print("""
class MpTest:
    policies = [
        api.AcceptLink(filters=[
                api.f.perimeter,
                api.f.endpoint("zone", "%s", who="server"),
                api.f.endpoint("app", "%s", who="server"),
                api.f.endpoint("process", "%s", who="server"),
            ], changes=[
                ("client", "network", "0.0.0.0"),
                ("client", "mask", 0),
            ]),
    ]
""" % (self.server.zone, self.server.app, self.server.process))
            return

        if self.ltype == "NAE":
            print("""
class MpTest:
    policies = [
        api.AcceptLink(filters=[
                api.f.ltype("NAE"),
                api.f.endpoint("app", "%s"),
                api.f.endpoint("process", "%s", who="client"),
                api.f.endpoint("dns_pattern", "%s", who="server"),
            ], changes=[
                ("server", "dns_pattern", "%s"),
            ]),
    ]
""" % (self.client.app, self.client.process, self.server.dns_pattern, self.server.dns_pattern.replace(".", "\.")))
            return

        if self.ltype in ["AIN", "AEG"]:
            if self.client.zone == self.server.zone:
                print("""
class MpTest:
    policies = [
        api.AcceptLink(filters=[
                api.f.ltype(["AEG", "AIN"]),
                api.f.same_zone,
                api.f.endpoint("app", "%s", who="client"),
                api.f.endpoint("process", "%s", who="client"),
                api.f.endpoint("app", "%s", who="server"),
                api.f.endpoint("process", "%s", who="server"),
            ], changes=[
            ]),
    ]
""" % (self.client.zone, self.client.app, self.client.process, self.server.zone, self.server.app, self.server.process))
                return

            print("""
class MpTest:
    policies = [
        api.AcceptLink(filters=[
                api.f.ltype(["AEG", "AIN"]),
                api.f.endpoint("zone", "%s", who="client"),
                api.f.endpoint("app", "%s", who="client"),
                api.f.endpoint("process", "%s", who="client"),
                api.f.endpoint("zone", "%s", who="server"),
                api.f.endpoint("app", "%s", who="server"),
                api.f.endpoint("process", "%s", who="server"),
            ], changes=[
            ]),
    ]
""" % (self.client.zone, self.client.app, self.client.process, self.server.zone, self.server.app, self.server.process))
            return

        print("""
class MpTest:
    policies = [
        api.AcceptLink(filters=[
                api.f.ltype("INT"),
                api.f.endpoint("app", "%s", who="client"),
                api.f.endpoint("process", "%s", who="client"),
                api.f.endpoint("app", "%s", who="server"),
                api.f.endpoint("process", "%s", who="server"),
            ], changes=[
            ]),
    ]
""" % (self.client.app, self.client.process, self.server.app, self.server.process))

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
    zone2apps = {
        "dev": ["cassandra"],
        "ops": ["cassandra"],
        "prod": ["dmzvm", "bendvm"],
        "nightly": ["dmzvm", "bendvm"],
        "prod-k8s": ["k8s", "kube-system", "monitoring", "prod-araali-operator", "prod-bend"],
        "nightly-k8s": ["k8s", "kube-system", "monitoring", "prod-araali-operator", "prod-bend"],
    }
    zone_apps = None

    def get_zone_apps(full=False):
        Runtime.zone_apps = {}
        for za in araalictl.get_zones():
            Runtime.zone_apps[za["name"]] = za["apps"]
        return Runtime.zone_apps

    def __init__(self):
        self.zones = None

    def refresh(self):
        if Runtime.zone2apps:
            Runtime.zone_apps = Runtime.zone2apps
            if self.zones == None:
                self.zones = [Zone(z) for z in Runtime.zone2apps.keys()]
            else:
                for z in self.zones:
                    z.refresh()
        else:
            Runtime.get_zone_apps()
            self.zones = [Zone(z) for z in Runtime.zone_apps.keys()]

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
    def __init__(self, name):
        self.zone = name
        self.apps = [App(name, a) for a in Runtime.zone_apps[name]]

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



