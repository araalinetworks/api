import os
import yaml

from . import utils

g_debug = False

def login():
    os.system("tsh login --proxy=%s --auth=local --user=%s %s" % (
                utils.cfg["teleport_fqdn"],
                utils.cfg["teleport_user"],
                utils.cfg["teleport_fqdn"],
             ))

def logout():
    os.system("tsh logout --proxy=%s --auth=local --user=%s" % (
                utils.cfg["teleport_fqdn"],
                utils.cfg["teleport_user"],
             ))

def app_login(app):
    os.system("tsh app login %s" % (app))

def app_logout(app):
    os.system("tsh app logout %s" % (app))

def get_config(server, use_tsh=False, debug=False):
    rc = utils.run_command_logfailure("%sssh %s sudo cat /etc/teleport.yaml" % (
        "tsh " if use_tsh else "", server), debug=debug)
    assert rc[0]
    cfg = yaml.load(rc[1], yaml.SafeLoader)
    if "Warning" in cfg: del cfg["Warning"]
    return cfg

def set_config(server, cfg):
    rc = os.system("ssh %s \"cat << 'EOF' > teleport.yaml\n%s\nEOF\"" % (server, yaml.dump(cfg)))
    assert rc == 0
    rc = os.system("ssh %s sudo mv teleport.yaml /etc/teleport.yaml" % (server))
    assert rc == 0
    rc = os.system("ssh %s sudo systemctl restart teleport" % (server))
    assert rc == 0

def add_svc(server, name, uri):
    cfg = get_config(server, True)
    cfg["app_service"]["enabled"] = True
    cfg["app_service"]["debug_app"] = False
    if name in [a["name"] for a in cfg["app_service"]["apps"]]:
        print("*** app already exists:\n%s" % yaml.dump([a for a in cfg["app_service"]["apps"] if name == a["name"]]))
        return
    cfg["app_service"]["apps"].append({
            "name": name,
            "uri": uri, # e.g. http://localhost:8080/
            "public_addr": "",
            "insecure_skip_verify": False,
        })
    print(yaml.dump(cfg["app_service"]))

def install(server):
    rc = utils.run_command_logfailure("ssh %s cat /etc/os-release" % server, debug=g_debug)
    assert rc[0]
    id_like = [a for a in rc[1].strip().split("\n") if "ID_LIKE" in a][0].rsplit("=", 1)[-1].split()

    print("Installing teleport on %s: %s" % (server, id_like))
    
    # get cmd from teleport, e.g: https://example.com/web/discover
    rc = os.system("ssh %s << 'EOF'\n%s\nEOF" % (server, input("enter cmd> ")))
    assert rc == 0
    
    cfg = get_config(server)
    cfg["teleport"]["nodename"] = server
    
    set_config(server, cfg)
