from . import utils
import requests

MAX_RETRIES = 5

def create_tenant_and_token(email):
    host = "https://console-%s.aws.araalinetworks.com" % utils.cfg["backend"]
    # Make request to quickstart backend to create tenant and fetch workloadYaml
    for x in range(MAX_RETRIES):
        rc = requests.post("%s/%s" % (host, "quickstart/v1/createTenantAndToken"),
                        json={'email': email})           
        if rc.status_code == 200:
            break
        if x >= MAX_RETRIES - 1:
            print("Error: Max retries exceeded. Could not create quickstart tenant")
            return False, None, None
    # Response validation
    resp_json = rc.json()
    if "tenant_id" not in resp_json or not "api_token" in resp_json:
        print("Error: Invalid quickstart server response")
        return False, None, None
    tenant_id = resp_json["tenant_id"]
    api_token = resp_json["api_token"]
    return True, tenant_id, api_token

def generate_workload_yaml(api_token, workload_name, tenant_id):
    host = "https://api-%s.aws.araalinetworks.com" % utils.cfg["backend"]
    headers = {"Authorization": "Bearer %s" % api_token}
    data = {"workload_name": workload_name, "tenant.id": tenant_id, "yaml_type": "2"}
    rc = requests.get("%s/%s" % (host, "api/v2/createFortifyYaml"), params=data, headers=headers)
    if rc.status_code != 200:
        return None, False
    resp_json = rc.json()
    if "workload_yaml" not in resp_json:
        print("Invalid response from apiserver, workload_yaml not present")
        return None, False
    return resp_json["workload_yaml"], True