import copy
import ipaddress
import json
import re
import yaml

try:
    import pandas as pd
    pd.set_option("display.max_colwidth", 400) # was 50
    pd.set_option("display.max_rows", 1000)
except:
    pass

import araalictl


def link_stats(runlink, all=False, only_new=True):
    defined, alerts, linktype_dict = 0, 0, {}
    for a in runlink:
        if not all and a.state == "DEFINED_POLICY": continue
        if only_new and a.new_state is not None: continue
        if a.state == "DEFINED_POLICY":
            defined += 1
        if a.state == "BASELINE_ALERT":
            alerts += 1
        linktype_dict[a.type] = linktype_dict.get(a.type, 0) + 1
    out = [{"what": "defined", "count": defined}, {"what": "alerts", "count": alerts}]
    for t, v in linktype_dict.items():
        out.append({"what": "link."+t, "count": v})
    return out

def dns_stats(runlink, all=False, only_new=False):
    pattern_dict = {}
    for a in runlink:
        if not all and a.state == "DEFINED_POLICY": continue
        if only_new and a.new_state is not None: continue
        if a.type != "NAE": continue
        for p in a.server.to_data().get("dns_pattern", "").split(":"):
            if not p or p in [".*"]: continue
            pattern_dict[p] = pattern_dict.get(p, 0) + 1
    keys = list(pattern_dict.keys())
    keys.sort(key=lambda x: -pattern_dict[x])
    out = []
    for k in keys:
        out.append({"dns": k, "count": pattern_dict[k]})
    return out


class Process(object):
    def __init__(self, data):
        self.zone = data["zone"]
        self.app = data["app"]
        self.process = data["process"]
        self.binary_name = data["binary_name"]
        self.parent_process = data.get("parent_process", None)

    def __repr__(self):
        return json.dumps(self.to_data())

    def to_data(self):
        if self.zone:
            obj = {"zone": self.zone, "app": self.app,                             
                "process": self.process,                                        
                "binary_name": self.binary_name,                                 
                "parent_process": self.parent_process}  
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

    def to_lib(self, zone, app):
        self.zone = zone
        app_parts = self.app.split(".")
        app_parts[0] = app
        self.app = ".".join(app_parts)


class NonAraaliClient(object):
    def __init__(self, data):
        self.process = None
        self.subnet = ipaddress.ip_address(str(data["subnet"]))
        self.netmask = data.get("netmask", 0)
        self.private_subnet = data.get("private_subnet", False)
        self.endpoint_group = data.get("endpoint_group", "")

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
        obj = {"subnet": str(self.subnet), "netmask": self.netmask, "endpoint_group": self.endpoint_group}
        for attr in dir(self):
            if "orig_" == attr[:len("orig_")]:
                obj[attr] = getattr(self, attr)
        return obj

    def to_lib(self, zone, app):
        pass


class NonAraaliServer(object):
    def __init__(self, data):
        self.process = None
        self.dst_port = data["dst_port"]
        self.private_subnet = False
        if "dns_pattern" in data:
            self.dns_pattern = data["dns_pattern"]
        else:
            self.dns_pattern = None
            self.subnet = ipaddress.ip_address(str(data["subnet"]))
            self.netmask = data.get("netmask", 0)
            self.private_subnet = data.get("private_subnet", False)
        self.endpoint_group = data.get("endpoint_group", "")

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
            obj = {"dns_pattern": self.dns_pattern, "dst_port": self.dst_port, "endpoint_group": self.endpoint_group}
        else:                                                                   
            obj = {"subnet": str(self.subnet), "netmask": self.netmask, "dst_port": self.dst_port, "endpoint_group": self.endpoint_group}

        for attr in dir(self):
            if "orig_" == attr[:len("orig_")]:
                obj[attr] = getattr(self, attr)
        return obj

    def to_lib(self, zone, app):
        pass


class AcceptLink:                                                               
    def __init__(self, filters, changes=[]):                                    
        self.filters = filters                                                  
        self.changes = changes                                                  
                                                                                
    def apply(self, links):                                                     
        l = LinkTable(links, f.new_state(None), *self.filters)                                     
        l.accept()                                                              
        for c in self.changes:                                                       
            l.change(*c)

        for link in l.links:
            if hasattr(link.server, "dns_pattern") and link.server.dns_pattern:
                link.server.change("dns_pattern", ".*" + link.server.dns_pattern + ".*")
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
                    l.policy = pname
                    count += 1
            print("%-20s matched %s rows" % (pname, count))
        return self

    def review(self, *filters, **kwargs):
        todo = kwargs.get("todo", False)
        filters = [a.__name__ for a in filters]
        def impl():
            for l in self.links:
                if todo:
                    if l.state == "DEFINED_POLICY" or l.new_state is not None:
                        continue
                else:
                    if l.new_state is None:
                        continue
                    if filters and l.policy not in filters:
                        continue
                yield l
        ret = list(impl()) 
        print("\nReviewing %s rows %s" % (len(ret), "that matched" if not todo else "that didn't match"))
        return ret
    

def check_notebook():
    try:
        return get_ipython().has_trait('kernel')
    except:
        return False

class Table(object):
    in_notebook = check_notebook()

    @classmethod
    def transform(cls, a):
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

        @classmethod
        def state(cls, state):
            """Valid states are: NAI, NAE, INT, AIN, AEG"""
            if isinstance(state, list):
                return lambda r: r.get("state", None) in state
            return lambda r: r.get("state", None) == state

        @classmethod
        def type(cls, link_type):
            if isinstance(link_type, list):
                return lambda r: r.get("type", None) in link_type
            return lambda r: r.get("type", None) == link_type

        @classmethod
        def new_state(cls, state):
            if isinstance(state, list):
                return lambda r: r.get("new_state", None) in state
            return lambda r: r.get("new_state", None) == state

        @classmethod
        def speculative(cls, state):
            if isinstance(state, list):
                return lambda r: r.get("speculative", None) in state
            return lambda r: r.get("speculative", None) == state

        @classmethod
        def endpoint(cls, field, val, flags=0, who="either"):
            """flags=re.IGNORECASE can be used"""
            def match_str(t, v):
                return re.search(t, v, flags=flags)

            def match_list(t, v):
                return any([match_val(a, v) is not None for a in t])

            def match_nonstr(t, v):
                return t == v

            def match_val(t, v):
                if isinstance(t, list):
                    return match_list(t, v)
                return match_str(t, v) if isinstance(t, str) else match_nonstr(t, v)

            def match(r):
                def get_default():
                    if isinstance(val, str):
                        return ""
                    if isinstance(val, list):
                        if isinstance(val[0], str):
                            return ""
                    return None
                defval = get_default()
                c = r.get("client", {}).get(field, defval)
                s = r.get("server", {}).get(field, defval)
                if who == "client":
                    return match_val(val, c)
                elif who == "server":
                    return match_val(val, s)
                else: # match either
                    return match_val(val, c) or match_val(val, s)
                return  False
            return match

        @classmethod
        def perimeter(cls, r):
            return r.get("client", {}).get("subnet", None) != None

        @classmethod
        def server_non_ip(cls, r):
            s = r.get("server", {})
            return s.get("dns_pattern", "")[:3] != "ip-" and s.get("subnet", None) == None

        @classmethod
        def same_zone(cls, r):
            return r.get("client", {}).get("zone", None) == r.get("server", {}).get("zone", None)

    def to_data(self):
        def transform(obj):
            obj = Table.transform(obj)
            if "unique_id" in obj: del obj["unique_id"]
            if "timestamp" in obj: del obj["timestamp"]
            return obj
        return [transform(a) for a in self.links]

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
        self.client = (Process if "zone" in data["client"] else NonAraaliClient)(data["client"])
        self.server = (Process if "zone" in data["server"] else NonAraaliServer)(data["server"])
        self.type = data["type"]
        self.speculative = data["speculative"]
        self.state = data["state"]
        self.timestamp = data["timestamp"]
        self.unique_id = data["unique_id"]
        self.new_state = None

    def to_data(self):                                                          
        obj = {}                                                                
        obj["client"] = self.client.to_data()
        obj["server"] = self.server.to_data()
        obj["type"] = self.type                                                
        obj["speculative"] = self.speculative                                   
        obj["state"] = self.state                                              
        obj["timestamp"] = self.timestamp                                       
        obj["unique_id"] = self.unique_id                                        
        obj["new_state"] = self.new_state                                        
        if hasattr(self, "policy"):
            obj["meta_policy"] = self.policy
        return obj 

    def accept(self):
        self.new_state = "DEFINED_POLICY"

    def snooze(self):
        self.new_state = "SNOOZED_POLICY"

    def meta_policy(self):
        if self.type == "NAI":
            print("""
class MpTest:
    policies = [
        api.AcceptLink(filters=[
                api.f.perimeter,
                api.f.endpoint("zone", "%s", who="server"),
                api.f.endpoint("app", "%s", who="server"),
                api.f.endpoint("process", "%s", who="server"),
            ], changes=[
                ("client", "subnet", "0.0.0.0"),
                ("client", "netmask", 0),
            ]),
    ]
""" % (self.server.zone, self.server.app, self.server.process))
            return

        if self.type == "NAE":
            if self.server.dns_pattern:
                print("""
class MpTest:
    policies = [
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("app", "%s"),
                api.f.endpoint("process", "%s", who="client"),
                api.f.endpoint("dns_pattern", "%s", who="server"),
            ], changes=[
                ("server", "dns_pattern", "%s"),
            ]),
    ]
""" % (self.client.app, self.client.process, self.server.dns_pattern, self.server.dns_pattern.replace(".", "\.")))
            else:
                print("""
class MpTest:
    policies = [
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("app", "%s"),
                api.f.endpoint("process", "%s", who="client"),
                api.f.endpoint("subnet", "%s", who="server"),
                api.f.endpoint("netmask", "%s", who="server"),
                api.f.endpoint("dst_port", "%s", who="server"),
            ], changes=[
                ("server", "subnet", "%s"),
            ]),
    ]
""" % (self.client.app, self.client.process, self.server.subnet, self.server.netmask, self.server.dst_port, self.server.subnet))

            return

        if self.type in ["AIN", "AEG"]:
            if self.client.zone == self.server.zone:
                print("""
class MpTest:
    policies = [
        api.AcceptLink(filters=[
                api.f.type(["AEG", "AIN"]),
                api.f.same_zone,
                api.f.endpoint("app", "%s", who="client"),
                api.f.endpoint("process", "%s", who="client"),
                api.f.endpoint("app", "%s", who="server"),
                api.f.endpoint("process", "%s", who="server"),
            ], changes=[
            ]),
    ]
""" % (self.client.app, self.client.process, self.server.app, self.server.process))
                return

            print("""
class MpTest:
    policies = [
        api.AcceptLink(filters=[
                api.f.type(["AEG", "AIN"]),
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
                api.f.type("INT"),
                api.f.endpoint("app", "%s", who="client"),
                api.f.endpoint("process", "%s", who="client"),
                api.f.endpoint("app", "%s", who="server"),
                api.f.endpoint("process", "%s", who="server"),
            ], changes=[
            ]),
    ]
""" % (self.client.app, self.client.process, self.server.app, self.server.process))

    def to_lib(self, zone, app):
        if self.type == "INT":
            self.client.to_lib(zone, app)
            self.server.to_lib(zone, app)
        elif self.type == "NAE" or self.type == "AEG":
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
    zone2apps = None
    zone_apps = {}
    zone_app_links = {}

    def get_zone_apps(hard=False, full=False, tenant=None):
        if hard:
            Runtime.zone_apps = {}
            for za in araalictl.get_zones(tenant=tenant, full=full):
                if not za["zone_name"]:
                    continue
                Runtime.zone_apps[za["zone_name"]] = []
                for a in za["apps"]:
                    if a["app_name"] == "invalid": continue
                    Runtime.zone_apps[za["zone_name"]].append(a["app_name"])
                    if full:
                        Runtime.zone_app_links[(za["zone_name"], a["app_name"])] = a.get("links", [])
        return list({"name":k, "Apps":v} for k,v in Runtime.zone_apps.items())

    def __init__(self, tenant=None):
        self.tenant = tenant
        self.zones = None

    def refresh(self):
        if Runtime.zone2apps:
            Runtime.zone_apps = Runtime.zone2apps
            if self.zones == None:
                self.zones = [Zone(z, tenant=self.tenant) for z in Runtime.zone2apps.keys()]
            else:
                for z in self.zones:
                    z.refresh(tenant=self.tenant)
        else:
            Runtime.get_zone_apps(hard=True, tenant=self.tenant, full=True)
            self.zones = [Zone(z, tenant=self.tenant, hard=False) for z in Runtime.zone_apps.keys()]

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


    def link_stats(self, all=False, only_new=True, runlink=None):
        if not runlink: runlink = self.iterlinks()
        return link_stats(runlink, all, only_new)

    def dns_stats(self, all=False, only_new=False, runlink=None):
        if not runlink: runlink = self.iterlinks()
        return dns_stats(runlink, all, only_new)

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
    def __init__(self, name, tenant=None, hard=True):
        self.tenant = tenant
        self.zone = name
        self.apps = [App(name, a, tenant=tenant, hard=hard) for a in Runtime.zone_apps.get(name, [])]

    def refresh(self, hard=True):
        for a in self.apps:
            a.refresh(hard)
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

    def __init__(self, zone, app, tenant=None, hard=True):
        self.tenant = tenant
        self.zone = zone
        self.app = app
        self.refresh(hard) # get links

    def refresh(self, hard=True):
        self.links = []
        if not hard and (self.zone, self.app) in Runtime.zone_app_links:
            for link in Runtime.zone_app_links[(self.zone, self.app)]:
                self.links.append(Link(link, self.zone, self.app))
        else:
            for link in araalictl.get_links(self.zone, self.app, tenant=self.tenant):
                self.links.append(Link(link, self.zone, self.app))
        return self
        
    def link_stats(self, all=False, only_new=True, runlink=None):
        if not runlink: runlink = self.iterlinks()
        return link_stats(runlink, all, only_new)

    def dns_stats(self, all=False, only_new=False, runlink=None):
        if not runlink: runlink = self.iterlinks()
        return dns_stats(runlink, all, only_new)

    def iterlinks(self, lfilter=None, pfilter=None, cfilter=False, afilter=False, dfilter=False, data=False):
        """lfilter for type, pfilter for process, cfilter for changes/dirty
           afilter for alerts, dfilter for defined
        """
        def impl():
            for l in self.links:
                if lfilter and l.type != lfilter:
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
                     if l.state != "BASELINE_ALERT" or l.type == "NAI" and l.speculative:
                        continue
                if dfilter: # show only defined
                     if l.state != "DEFINED_POLICY":
                        continue
                yield l
        if data:
            return [a.to_data() for a in impl()]
        return list(impl())

    def commit(self):
        """accept policy etc backend calls"""
        return araalictl.update_links(self.zone, self.app, self.review(data=True), tenant=self.tenant)

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
                if link.state == "BASELINE_ALERT" and link.type == "NAI" and link.speculative:
                    continue # skip baseline alerts
                link_type.setdefault(link.type, {}).setdefault(link.state, []).append(1)                      

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
            link.to_lib(zone, app)

    def __repr__(self):
        return json.dumps(self.to_data())
