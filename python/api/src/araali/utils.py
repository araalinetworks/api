from __future__ import print_function

import os
import shlex
import subprocess
import yaml

cfg_fname = os.environ['HOME']+"/.araalirc"

def read_config():
    if os.path.isfile(cfg_fname):
        with open(cfg_fname, "r") as f:
            cfg = yaml.load(f, Loader=yaml.SafeLoader)
    else:
        cfg = {}

    if not cfg.get("tenant", None): cfg["tenant"] = None
    if not cfg.get("template_dir", None): cfg["template_dir"] = "../templates"
    if not cfg.get("token", None): cfg["token"] = os.getenv('ARAALI_API_TOKEN')
    if not cfg.get("backend", None): cfg["backend"] = "prod"
    # env variable overrides on disk config
    if os.getenv("ARAALI_BACKEND"):
        cfg["backend"] = os.getenv("ARAALI_BACKEND")
    return cfg

cfg = read_config()

def config(tenant=None, tenants=None, template_dir=None, backend=None):
    global cfg

    def save(cfg):
        with open(cfg_fname, "w") as f:
            cfg2 = dict(cfg)
            del cfg2["token"]
            yaml.dump(cfg2, f)

    if tenant is not None:
        if not tenant: # passed as empty string
            tenant = None # store it as nil in yaml
        cfg["tenant"] = tenant
        save(cfg)
    if tenants is not None:
        cfg["tenants"] = [dict(zip(["name", "id"], a.split(":"))) for a in tenants.split(",")]
        save(cfg)
    for k in ["template_dir", "backend"]:
        if eval(k) is not None:
            cfg[k] = eval(k)
            save(cfg)
    print(yaml.dump(cfg))

def get_by_key(o, k):
    k = k.split(".")
    for a in k:
        o = o.get(a, None)
        if o is None: return "None"
    return o if o is not None else "None"

def dump_table(objs, quiet=False, filterby=None, countby=None, groupby=None):
    class FilterBy(object):
        def __init__(self, filterby):
            if filterby:
                self.filterby = [a.split("=") for a in filterby.split(":")]
            else:
                self.filterby = None
        
        def filter(self, o):
            if self.filterby is None: return True

            match_count = 0
            for f in self.filterby:
                k, v = f
                for a in v.split(","): # like an OR
                    if get_by_key(o, k) == a:
                        match_count += 1
                        break
            # matched all filters, like AND
            if match_count == len(self.filterby):
                return True
            return False

    class CountBy(object):
        def __init__(self, countby, groupby):
            self.countby = countby.split(",") if countby else countby
            self.groupby = groupby.split(",") if groupby else groupby
            if countby:
                if groupby is None:
                    self.groupby_dict = {"global": {}}
                    for c in self.countby:
                        self.groupby_dict["global"][c] = set()
                else:
                    self.groupby_dict = {}

        def count(self, o):
            if self.countby:
                if self.groupby:
                    groupby_key = []
                    for g in self.groupby:
                        groupby_key.append(get_by_key(o, g))
                    groupby_key = ":".join(groupby_key)
                    if groupby_key not in self.groupby_dict:
                        self.groupby_dict[groupby_key] = {}
                        for c in self.countby:
                            self.groupby_dict[groupby_key][c] = set()
                else:
                    groupby_key = "global"

                for k,v in self.groupby_dict[groupby_key].items():
                    v.add(get_by_key(o, k))

        def show(self):
            if not self.countby:
                return

            for g, countby_dict in self.groupby_dict.items():
                print("\n")
                print("="*40, "%s" % g, "="*40)
                if countby:
                    for k,v in countby_dict.items():
                        print("%ss: %s" % (k, len(v)))

    countby = CountBy(countby, groupby)
    filterby = FilterBy(filterby)
    for idx, o in enumerate(objs):
        if not filterby.filter(o): continue
        if not quiet:
            print("%s %s %s" % ("="*40, idx, "="*40))
            print(yaml.dump(o))
        countby.count(o)
    countby.show()


def make_map(kvstr):
    k, v = kvstr.split("=")
    return k, int(v)

def eprint(*args, **kwargs):
    args = [a.decode() for a in args]
    print(*args, file=sys.stderr, **kwargs)

def run_command(command, result=False, strip=True, in_text=None, debug=False, env=os.environ):
    def collect_output(ret, output):
        if output:
            if strip:
                output = output.strip()
            if result:
                ret.append(output.decode())
            else:
                eprint(output)

    if debug:
        print(command, result)
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE,
                                stdin=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=env)
    ret = []
    if result:
        if in_text:
            outs, errs = process.communicate(input=in_text.encode())
        else:
            outs, errs = process.communicate()
        return process.poll(), outs+errs
    else:
        while True:
            rc = process.poll()
            err = process.stderr.readline()
            out = process.stdout.readline()
            if rc is not None and not out and not err:
                return rc, "\n".join(ret)
            collect_output(ret, out)
            collect_output(ret, err)
