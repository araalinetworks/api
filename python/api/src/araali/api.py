import datetime
import grpc
import os
import yaml

from . import araali_api_service_pb2
from . import araali_api_service_pb2_grpc

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

def init_alertreq():
    req = araali_api_service_pb2.ListAlertsRequest()
    
    # XXX: default it to None, and pick up from rc file
    req.tenant.id = cfg["tenant"]
    
    req.filter.open_alerts = True
    req.filter.closed_alerts = False
    req.filter.list_all_alerts = True
    req.filter.perimeter_ingress = True
    req.filter.perimeter_egress = True
    req.filter.home_non_araali_ingress = True
    req.filter.home_non_araali_egress = True
    req.filter.araali_to_araali = True
    req.filter.time.start_time.FromDatetime(datetime.datetime(year=2012,day=2,month=2))
    req.filter.time.end_time.FromDatetime(datetime.datetime.now())
    
    req.count = 10
    print(req)

    return req

class API:
    def __init__(self):
        global cfg
        if cfg["token"] is None:
            raise Exception("*** ARAALI_API_TOKEN environment variable is not set")

        class GrpcAuth(grpc.AuthMetadataPlugin):
            def __init__(self, key):
                self._key = key

            def __call__(self, context, callback):
                callback((('authorization', self._key),), None)

        token_cred = grpc.metadata_call_credentials(GrpcAuth("Bearer %s" % cfg["token"]))
        channel_cred = grpc.ssl_channel_credentials()
        creds = grpc.composite_channel_credentials(channel_cred, token_cred)

        backend = cfg["backend"]
        if not backend:
            backend = "prod"
        channel = grpc.secure_channel('api-%s.aws.araalinetworks.com:443' % (backend), creds)

        self.stub = araali_api_service_pb2_grpc.AraaliAPIStub(channel)

    def get_alerts(self):
        """Fetches alerts
            Usage: alerts, next_page, status = api.get_alerts()
        """
        resp = self.stub.listAlerts(init_alertreq())
        if resp.response.code != 0:
            print("*** Error fetching alerts:", resp.response.message)
        return (resp.links, resp.paging_token, resp.response.code)
