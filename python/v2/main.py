#!/usr/bin/env python

import grpc
import araali_api_service_pb2
import araali_api_service_pb2_grpc

token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21lcklEIjoibWV0YS10YXAiLCJlbWFpbCI6InZhbXNpQGFyYWFsaW5ldHdvcmtzLmNvbSIsImV4cCI6MTY4Njc5MjI5MiwiaWF0IjoxNjU1MjU2MjkyLCJqdGkiOiI4d2k1YUsyUTgydjdneWRSV0xBUXpRIiwibmJmIjoxNjU1MjU2MjkyLCJybGlzdCI6ImRvY3MsaW50ZXJhY3QiLCJyb2xlIjoiQXJhYWxpQWRtaW4ifQ.Q_Aj_DxJZwE-eL4UwIcQQWxX3WMcipQZL70Fzha37DZ9KeZqImjbq8drYEBxwYr81AuDluptEC7QQkZ6zHF18ICdb4ItBldxHXxQ-yYqGyIYoUmrP_RzFapM9DbWmmnNhCJgK1W_phzcJQ8FH4jlXXhKBTvn7mXtysMv06clnumqoIXtJrPu9X8j78yPVMScelTACoqmrLWUMavJYnSGe1O0vHEXVe9yjkIyUijILKInnmBbXfX8aJBqa0HD8P5KyKkazOMkbkkW87dC3KxcbfH54-2qKtF7jhW5jzvd5ozD86qIZ9PFvxtJ3mEoc2YB63Ec7pcuNSrZaAby7otrXBZAEOwEt83UFbh9AAlnV8KQ_HBVhxrwCvagUdDtY0SrSXtYCLEBQd2dKat2cahKRc8RIOAvS__PkDwb9Zd7RH4Uo6bxT4BaLkcY5keO9RGy7AU0wNYHf2pkGAs7rPaFnv0ABBgSkpZADa3WcyKF_cZxqGp1B1MXtciAD-3dHP0s9iKMqwYNaZyI7qG6gB3IH5ju5o_OtrOycNM2CNH_yraxX_20gOqkc5FtP-7TSisBJMziVBzGVvz-8u0oR9zZHyx4tAWUjCCrsFs2pYYk23pqLrtnsF6T2E4xz81Tl8ZyiYghfqn9kWPrkDpOa6JUi4XLMPNaZ7v8dp12bpE3ysk"

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
