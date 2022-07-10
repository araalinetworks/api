#!/usr/bin/env python

import grpc
import araali_api_service_pb2
import araali_api_service_pb2_grpc

token = ""

# Setup "authorization: Bearer: <token>"
token_cred = grpc.access_token_call_credentials(token)
channel_cred = grpc.ssl_channel_credentials()
creds = grpc.composite_channel_credentials(channel_cred, token_cred)

channel = grpc.secure_channel('api-nightly.aws.araalinetworks.com:443', creds)

try:
    stub = araali_api_service_pb2_grpc.AraaliAPIStub(channel)
except Exception as ex:
    print('Exception in connecting to API server: %s' % ex)

req = araali_api_service_pb2.ListAlertsRequest()
req.tenant.id = "meta-tap"
req.count = 10

try:
    resp = stub.listAlerts(req)
except Exception as ex:
    print('Exception in calling API: %s' % ex)

print(resp)
