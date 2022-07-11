import datetime
import grpc
import os

from . import araali_api_service_pb2
from . import araali_api_service_pb2_grpc

class API:
    def __init__(self):
        token = os.getenv('ARAALI_API_TOKEN')
        if token is None:
            raise Exception("*** ARAALI_API_TOKEN environment variable is not set")

        req = araali_api_service_pb2.ListAlertsRequest()

        req.tenant.id = "meta-tap"

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
        self.req = req

        class GrpcAuth(grpc.AuthMetadataPlugin):
            def __init__(self, key):
                self._key = key

            def __call__(self, context, callback):
                callback((('authorization', self._key),), None)

        token_cred = grpc.metadata_call_credentials(GrpcAuth("Bearer %s" % token))
        channel_cred = grpc.ssl_channel_credentials()
        creds = grpc.composite_channel_credentials(channel_cred, token_cred)

        channel = grpc.secure_channel('api-nightly.aws.araalinetworks.com:443', creds)

        self.stub = araali_api_service_pb2_grpc.AraaliAPIStub(channel)

    def get_alerts(self):
        """Fetches alerts
            Usage: alerts, next_page, status = api.get_alerts()
        """
        resp = self.stub.listAlerts(self.req)
        if resp.response.code != 0:
            print("*** Error fetching alerts:", resp.response.message)
        return (resp.links, resp.paging_token, resp.response.code)
