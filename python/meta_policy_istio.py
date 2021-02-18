import api

class MpIstio:
    policies = [
        api.AcceptLink(filters=[
            api.f.type("INT"),
            api.f.same_pod,
            api.f.endpoint("process", "pilot-agent", who="client"),
            api.f.endpoint("process", "envoy", who="server"),
        ], changes=[
        ]),
        api.AcceptLink(filters=[
            api.f.type("INT"),
            api.f.endpoint("process", "envoy", who="client"),
            api.f.endpoint("process", "envoy", who="server"),
        ], changes=[
        ]),
        api.AcceptLink(filters=[
            api.f.type("INT"),
            api.f.same_pod,
            api.f.endpoint("process", ["application.jar"], who="client"),
            api.f.endpoint("process", "envoy", who="server"),
        ], changes=[
        ]),
        api.AcceptLink(filters=[
            api.f.type("INT"),
            api.f.same_pod,
            api.f.endpoint("process", ["pilot-agent", "envoy"], who="client"),
            api.f.endpoint("process", ["application.jar"], who="server"),
        ], changes=[
        ]),
        api.AcceptLink(filters=[
            api.f.type("INT"),
            api.f.self_loop,
        ], changes=[
        ]),
        api.AcceptLink(filters=[
            api.f.type("AEG"),
            api.f.endpoint("process", ["kubelet"], who="client"),
        ], changes=[
        ]),
        api.AcceptLink(filters=[
            api.f.type(["AEG", "AIN"]),
            api.f.same_zone,
            api.f.endpoint("app", "kube-system.metrics-server-", who="client"),
            api.f.endpoint("process", "metrics-server", who="client"),
            api.f.endpoint("process", ["kubelet", "pilot-agent", "sidecar-injector"], who="server"),
        ], changes=[
        ]),
        api.AcceptLink(filters=[
            api.f.type(["AEG", "AIN"]),
            api.f.same_zone,
            api.f.endpoint("process", "envoy", who="client"),
            api.f.endpoint("process", "pilot-discovery", who="server"),
        ], changes=[
        ]),
    ]

print("Adding meta-policies to runner")
api.mpr.add(MpIstio)