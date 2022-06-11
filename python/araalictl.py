#!/usr/bin/env python
"""
Wrappers for araalictl for python use
"""
import datetime
import json
import os
import requests
import sys
from sys import platform
import yaml

from main import Usage, run_command

g_debug = False

def help():
    """get araalictl help"""
    print(run_command("%s -h" % (g_araalictl_path), result=True, debug=g_debug)[1])

def fetch():
    """For downloading and upgrading araalictl"""
    linux_url = "https://s3-us-west-2.amazonaws.com/araalinetworks.cf/araalictl-api.linux-amd64"
    darwin_url = "https://s3-us-west-2.amazonaws.com/araalinetworks.cf/araalictl-api.darwin-amd64"

    if platform == "linux" or platform == "linux2":
        url = linux_url
    elif platform == "darwin":
        url = darwin_url
    else:
        raise Usage("only linux and mac are currently supported")
    if not os.path.exists("araalictl"):
        print("Fetching araalictl ...")
        r = requests.get(url, allow_redirects=True)
        open('araalictl', 'wb').write(r.content)
        os.chmod('araalictl', 0o777)
    else:
        pass
        #print("upgrading araalictl ...")
        #run_command("sudo %s upgrade" % (g_araalictl_path))

g_araalictl_path = "./araalictl"

def set_araalictl_path(new_path):
    global g_araalictl_path
    g_araalictl_path = new_path

def auth(token):
    cmd = "sudo %s authorize -token=- -local" % (g_araalictl_path)
    rc = run_command(cmd, in_text=token, result=True, strip=False)
    assert rc[0] == 0, rc[1]

def deauth():
    cmd = "sudo %s authorize -clean" % g_araalictl_path
    rc = run_command(cmd, result=True, strip=False)
    assert rc[0] == 0, rc[1]

def alerts(start_time=None, token=None, count=200, end_time=None, tenant=None):
    """get alerts"""
    if token:
        cmd = "-paging-token %s" % token
    else:
        if start_time is None:
            start_time = datetime.datetime.now() - datetime.timedelta(days=1)
        if type(start_time) == datetime.datetime:
            start_time = int(start_time.timestamp())
        cmd = "-starttime %s" % (start_time)
        if end_time is None:
            end_time = datetime.datetime.now() - datetime.timedelta(days=1)
        if type(end_time) == datetime.datetime:
            end_time = int(end_time.timestamp())
        cmd += " -endtime %s" % (end_time)

    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s api -fetch-alerts %s -count %s %s" % (
                        g_araalictl_path, cmd, count, tstr),
                     debug=g_debug, result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def monitor(on=True, zone=None, app=None, service=None, email=None, tenant=None):
    """monitor lens"""
    flags = ""
    if service: flags += " -service %s" % service
    else: flags += " -zone=%s -app=%s" % (zone, app)
    cmd = "subscribe-for-alert" if on else "unsubscribe-from-alert"

    tstr = " -tenant=%s " % (tenant) if tenant else ""
    tstr += " -email=%s " % (email) if email else ""
    rc = run_command("%s api -%s %s %s" % (
                     g_araalictl_path, cmd, flags, tstr), result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def star_lens(zone="", app="", service=None, email=None, tenant=None):
    """star lens"""
    flags = ""
    if service: flags += " -service %s" % service
    else: flags += " -zone=%s -app=%s" % (zone, app)

    tstr = " -tenant=%s " % (tenant) if tenant else ""
    tstr += " -email=%s " % (email) if email else ""
    rc = run_command("%s api -star-lens %s %s" % (
                     g_araalictl_path, flags, tstr), result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def unstar_all(email=None, tenant=None):
    """unstar all lenses"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    tstr += " -email=%s " % (email) if email else ""
    rc = run_command("%s api -clear-starred-lens %s" % (
                     g_araalictl_path, tstr), result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def assess(tenant=None):
    """get assessment report to fetch important lenses"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s assessment -report %s" % (
                     g_araalictl_path, tstr), result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def get_lenses(enforced=False, starred=False, tenant=None):
    """get lenses"""
    flags = ""
    if enforced: flags += " -enforced"
    if starred: flags += " -starred"

    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s api -fetch-enforcement-status %s %s" % (
                     g_araalictl_path, flags, tstr), result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def update_lens_owner(email=None, add=True, zone=None, app=None, service=None,
                      tenant=None):
    """update lens owner"""
    assert zone and app or service
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    tstr += " -email=%s " % (email) if email else ""
    flags = ""
    flags += " -owner-op=add " if add else " -owner-op=del "
    flags += " -service=%s " % (service) if service else " -zone=%s -app=%s " % (zone, app)
    rc = run_command("%s api -update-lens-owner %s %s" % (
                     g_araalictl_path, flags, tstr),
                     result=True, strip=False, debug=g_debug)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def get_starred(user_email=None, tenant=None):
    """show starred"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    tstr += " -email=%s " % (user_email) if user_email else ""
    rc = run_command("%s api -fetch-starred-lens %s" % (
        g_araalictl_path, tstr), result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def get_mapping(tenant=None):
    """get app remapping config"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s app-mapping -op list %s" % (
        g_araalictl_path, tstr), result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def add_mapping(data, tenant=None):
    """add app remapping config"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s app-mapping -op add %s" % (
        g_araalictl_path, tstr), in_text=yaml.dump(data), result=True,
        strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def rm_mapping(data, tenant=None):
    """rm app remapping config"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s app-mapping -op del %s" % (
        g_araalictl_path, tstr), in_text=yaml.dump(data), result=True,
        strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def rbac_show_roles(tenant=None):
    """show rbac"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s user-role -op list %s" % (
                     g_araalictl_path, tstr), result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def rbac_show_users(tenant=None):
    """show rbac"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s user-role -op list-user-roles %s" % (
                     g_araalictl_path, tstr), result=True, strip=False,
                     debug=g_debug)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def rbac_add_role(name, zone, app, tenant=None):
    """add new role"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s user-role -op=add -zone=%s -app=%s -name=%s %s" % (
                     g_araalictl_path, zone, app, name, tstr),
                     result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def rbac_del_role(name, tenant=None):
    """del role"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s user-role -op=del -name='%s' %s" % (
                     g_araalictl_path, name, tstr),
                     result=True, strip=False, debug=g_debug)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def rbac_create_user(email, name, tenant=None):
    """create user"""
    tstr = " -id=%s " % (tenant) if tenant else ""
    rc = run_command("%s tenant -op add-user -user-email='%s' -user-name='%s' %s" % (
                     g_araalictl_path, email, name, tstr),
                     result=True, strip=False, debug=g_debug)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def rbac_delete_user(email, name, tenant=None):
    """delete user"""
    tstr = " -id=%s " % (tenant) if tenant else ""
    rc = run_command("%s tenant -op del-user -user-email='%s' -user-name='%s' %s" % (
                     g_araalictl_path, email, name, tstr),
                     result=True, strip=False, debug=g_debug)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)


def rbac_assign_roles(email, roles, tenant=None):
    """assign a list of roles to email"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    roles = ",".join(roles)
    rc = run_command("%s user-role -op assign -user-email %s -roles %s %s" % (
                     g_araalictl_path, email, roles, tstr),
                     result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def rbac_unassign_roles(email, roles, tenant=None):
    """assign a list of roles to email"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    roles = ",".join(roles)
    rc = run_command("%s user-role -op deny -user-email %s -roles %s %s" % (
                     g_araalictl_path, email, roles, tstr),
                     result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)


def get_pod_apps(tenant=None):
    """Get zones and apps for tenant"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s api -list-pod-mappings %s" % (g_araalictl_path, tstr),
            result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)


def tenant_create(user_email, tenant_name="", user_name=""):
    """Create a subtenant"""
    cmd = "%s tenant -op=add -name=\"%s\" -user-email=%s -user-name=\"%s\"" % (
        g_araalictl_path, tenant_name, user_email, user_name)
    rc = run_command(cmd, result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def tenant_delete(tenant_id):
    """Delete a subtenant"""
    rc = run_command("%s tenant -op=del -id=%s" % (g_araalictl_path, tenant_id), result=True, strip=False)
    assert rc[0] == 0, rc[1]

def fog_setupconfig(tenant_id, dns_name, vpc_id, subnet_id, key_name,
                    dns_hosted_zone_id, instance_type="m5.large"):
    """Setup config required to install a fog"""
    rc = run_command("%s config -tenant=%s Fog=%s" % (g_araalictl_path, tenant_id, dns_name),
                     result=True, strip=False)
    assert rc[0] == 0, rc[1]

    cfg_str = "VPCIDParameter=%s,SubnetIDParameter=%s,KeyNameParameter=%s,HostedZoneParameter=%s,InstanceTypeParameter=%s,ReadOnlyRoleParameter=" % (
        vpc_id, subnet_id, key_name, dns_hosted_zone_id, instance_type)
    rc = run_command("%s config -tenant=%s InternalFogInstallParams=%s" % (g_araalictl_path, tenant_id, cfg_str),
                     result=True, strip=False)
    assert rc[0] == 0, rc[1]

def fog_install(tenant, force=False, nodes=None):
    """Install AWS mode fog"""
    cstr = " -nodes=%s " % (nodes) if nodes else ""
    cstr += " -force " if force else ""
    rc = run_command("%s install-fog -tenant=%s -mode=aws %s" %
                     (g_araalictl_path, tenant, cstr), result=True, strip=False)
    assert rc[0] == 0, rc[1]

def fog_uninstall(tenant_id):
    """Uninstall AWS mode fog"""
    rc = run_command("%s uninstall-fog -tenant=%s -mode=aws" % (g_araalictl_path, tenant_id),
                     result=True, strip=False)
    assert rc[0] == 0, rc[1]

def get_zones(full=False, tenant=None):
    """Get zones and apps for tenant"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s api -fetch-zone-apps %s %s" % (g_araalictl_path, "-full" if full else "", tstr),
            result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def get_pod_apps(tenant=None):
    """Get zones and apps for tenant"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s api -list-pod-mappings %s" % (g_araalictl_path, tstr),
            result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def push_pod_apps(data, tenant=None):
    """Get zones and apps for tenant"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s api -update-pod-mappings %s" % (g_araalictl_path, tstr),
            in_text=yaml.dump(data), result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)


def update_links(zone, app, data, tenant=None):
    """Update actions on a link"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    ret_val = {}
    for link in data:
        if link["new_state"] == "DEFINED_POLICY" or link["new_state"] == "DENIED_POLICY":
            ret_val["policies"] = ret_val.get("policies", 0) + 1
            if link["state"] == "BASELINE_ALERT":
                ret_val["alerts"] = ret_val.get("alerts", 0) + 1
    
        elif link["new_state"] == "SNOOZED_POLICY":
            if link["state"] == "BASELINE_ALERT":
                ret_val["alerts"] = ret_val.get("alerts", 0) + 1
            ret_val["policies"] = ret_val.get("policies", 0) + 1

    if not ret_val:
        ret_val['empty'] = {"success": "Empty policy request"}
    else:
        if g_debug: print(yaml.dump(data))
        rc = run_command("%s api -zone %s -app %s -update-links %s" % (g_araalictl_path, zone, app, tstr),
                         in_text=yaml.dump(data), result=True, strip=False)
        assert rc[0] == 0, rc[1]
        ret_val = json.loads(rc[1])

    return ret_val

def get_links(zone=None, app=None, service=None, tenant=None):
    """Get links for a zone and app"""
    assert service is not None or zone is not None and app is not None
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    if service:
        tstr += " -service=%s " % (service)
    else:
        tstr += " -zone=%s -app=%s " % (zone, app)

    rc = run_command("%s api -fetch-links %s" % (g_araalictl_path, tstr),
                     result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def get_fogs(tenant=None):
    """Get all fogs"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s api -fetch-fogs %s" % (
        g_araalictl_path, tstr), result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return json.loads(rc[1])

def get_agents(tenant=None):
    """Get all agents"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    for fog in get_fogs(tenant):
        rc = run_command("%s api -fetch-agents -agentid %s %s" % (
            g_araalictl_path, fog, tstr), result=True, strip=False)
        assert rc[0] == 0, rc[1]
        obj = json.loads(rc[1])
        for o in obj:
            yield {"agent": o, "fog": fog}

def get_apps(tenant=None):
    """Get all apps"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    for agent in get_agents(tenant):
        if agent["agent"][:len("ak8s.")] == "ak8s.": continue
        if agent["agent"] in ["invalid", "Unknown"]: continue
        rc = run_command("%s api -fetch-apps -agentid %s -fogid %s %s" % (
            g_araalictl_path, agent["agent"], agent["fog"], tstr), result=True, strip=False)
        if rc[0] != 0:
            print("*** %s: %s" % (agent["agent"], rc[1]))
            continue
        obj = json.loads(rc[1])
        for o in obj["apps"]:
            yield {"agent": agent["agent"], "fog": agent["fog"], "zone": obj["zone"], "app": o}

def ping(zone, app, dst, port, agent_id, tenant=None):
    """ping dst from src"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s api -ping=src=%s/%s,dst=%s:%s -agentid %s %s" % (
            g_araalictl_path, zone, app, dst, port, agent_id, tstr), result=True, strip=False)
    if rc[1].decode().strip() == "open":
        return True
    print("*** z=%s a=%s dst=%s port=%s agent=%s tenant=%s rc=%s" % (zone, app, dst, port, agent_id, tenant, rc))
    return False

def get_compute(zone, app, tenant=None):
    """Get compute for a zone and app"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    rc = run_command("%s api -zone %s -app %s -fetch-compute %s" % (
        g_araalictl_path, zone, app, tstr), result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return json.loads(rc[1])

def world(direction="ingress_world,egress_world", on=True, email=None,
          tenant=None):
    """Monitor perimeter ingress/egress"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    tstr += " -email=%s " % (email) if email else ""
    op = "subscribe-for-alert" if on else "unsubscribe-from-alert"

    rc = run_command("%s api -%s -direction=%s %s" % (
        g_araalictl_path, op, direction, tstr), debug=g_debug, result=True,
        strip=False)
    assert rc[0] == 0, rc[1]
    ret_val = json.loads(rc[1])

    return ret_val

def enforce(data, service=False, tenant=None):
    """Enforce zone app or service."""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    ostr = " -enforce-service " if service else " -enforce-zone-app "

    ret_val = {}
    if not data:
        ret_val['empty'] = {"success": "Empty enforcement request"}
    else:
        if g_debug:
            print(yaml.dump(data))
        rc = run_command("%s api %s %s" % (
            g_araalictl_path, ostr, tstr), in_text=yaml.dump(data), debug=g_debug, result=True, strip=False)
        assert rc[0] == 0, rc[1]
        ret_val = json.loads(rc[1])

    return ret_val

def fetch_flows(data, tenant=None):
    """Update actions on a link"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""

    if g_debug: print(yaml.dump(data))
    rc = run_command("%s api -fetch-flows %s" % (g_araalictl_path, tstr),
                     in_text=yaml.dump(data), result=True, strip=False)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def fetch_templates(public=False, template=None, tenant=None):
    """Fetch templates (or public ones)"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    tstr += " -public " if public else ""
    tstr += " -template=%s " % (template) if template else ""

    rc = run_command("%s api -list-templates %s" % (g_araalictl_path, tstr),
                     result=True, strip=False, debug=g_debug)
    assert rc[0] == 0, rc[1]
    return yaml.load(rc[1], yaml.SafeLoader)

def update_template(data, public=False, tenant=None):
    """Update template"""
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    if g_debug: print(yaml.dump(data))
    command = "-update-template" if not public else "-export-template"
    rc = run_command("%s api %s %s" % (g_araalictl_path, command, tstr),
                     in_text=yaml.dump(data), result=True, strip=False, debug=g_debug)
    assert rc[0] == 0, rc[1]
    ret_val = json.loads(rc[1])

    return ret_val

def template(data, save=False, use=False, name=None, tenant=None):
    tstr = " -tenant=%s " % (tenant) if tenant else ""
    tstr += " -multi-link-name=%s " % (name) if name else ""
    tstr += " -save-link-template " if save else ""
    tstr += " -use-link-template " if use else ""

    if g_debug: print(yaml.dump(data))
    rc = run_command("%s api -link-to-template %s" % (g_araalictl_path,
                     tstr), in_text=yaml.dump(data), result=True, strip=False)
    assert rc[0] == 0, rc[1]
    if save or use:
        return {"policies":"Success: true"}
    return yaml.load(rc[1].strip(), yaml.SafeLoader)

if __name__ == '__main__':
    sys.exit(fetch())
