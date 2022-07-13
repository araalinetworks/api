import os
import yaml

cfg_fname = os.environ['HOME']+"/.araalirc"

def read_config():
    if os.path.isfile(cfg_fname):
        with open(cfg_fname, "r") as f:
            cfg = yaml.load(f, Loader=yaml.SafeLoader)
            if not cfg.get("tenant", None): cfg["tenant"] = None
            if not cfg.get("template_dir", None): cfg["template_dir"] = "../templates"
            if not cfg.get("token", None): cfg["token"] = os.getenv('ARAALI_API_TOKEN')
            if not cfg.get("backend", None): cfg["backend"] = os.getenv('ARAALI_BACKEND')
            return cfg

    return {
            "tenant": None, "template_dir": "../templates",
            "token": os.getenv('ARAALI_API_TOKEN'),
            "backend": os.getenv("ARAALI_BACKEND")
           }

cfg = read_config()

def config(tenant=None, tenants=None, template_dir=None, backend=None, token=None):
    global cfg
    if tenant is not None:
        if not tenant: # passed as empty string
            tenant = None # store it as nil in yaml
        cfg["tenant"] = tenant
        with open(cfg_fname, "w") as f:
            yaml.dump(cfg, f)
    if tenants is not None:
        cfg["tenants"] = [dict(zip(["name", "id"], a.split(":"))) for a in tenants.split(",")]
        with open(cfg_fname, "w") as f:
            yaml.dump(cfg, f)
    for k in ["template_dir", "backend", "token"]:
        if eval(k) is not None:
            cfg[k] = eval(k)
            with open(cfg_fname, "w") as f:
                yaml.dump(cfg, f)
    print(yaml.dump(cfg))

def dump_table(objs):
    for idx, o in enumerate(objs):
        print("%s %s %s" % ("="*40, idx, "="*40))
        print(yaml.dump(o))

def make_map(kvstr):
    k, v = kvstr.split("=")
    return k, int(v)
