import api

class MpAraali:
    policies = [
        api.AcceptLink(filters=[
                api.f.endpoint("process", ["autok8s", "guarantor"], who="client"),
                api.f.endpoint("dns_pattern", ":.*.aws.araalinetworks.com:", who="server"),
            ], changes=[
                ("server", "dns_pattern", ":.*\.aws\.araalinetworks\.com:"),
            ]),
    ]
    
print("Adding meta-policies to runner")
api.mpr.add(MpAraali)
