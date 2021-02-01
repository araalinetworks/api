import api

class MpLacework:
    policies = [
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint('binary_name', '/var/lib/lacework/3.4.2/datacollector', who="client"),
                api.f.endpoint("subnet", "169.254.169.254", who="server"),
                api.f.endpoint("netmask", 32, who="server"),
                api.f.endpoint("dst_port", 80, who="server"),
            ], changes=[
            ]),
    ]
    
print("Adding meta-policies to runner")
api.mpr.add(MpLacework)
