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

def dump_table(objs):
    for idx, o in enumerate(objs):
        print("%s %s %s" % ("="*40, idx, "="*40))
        print(yaml.dump(o))

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
