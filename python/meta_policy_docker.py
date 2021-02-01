import api

class MpDockerd:
    policies = [
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("process", "dockerd", who="client"),
                api.f.endpoint("dns_pattern", [":quay.io:",
                                            ":production.cloudflare.docker.com:",
                                            ":quayio-production-s3.s3.amazonaws.com:",
                                          ], who="server"),
            ], changes=[
            ]),
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("process", "dockerd", who="client"),
                api.f.endpoint("dns_pattern", ":.*.docker.io:", who="server"),
            ], changes=[
                ("server", "dns_pattern", ".*:.*\.docker\.io:.*"),
            ]),
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("process", "dockerd", who="client"),
                api.f.endpoint("dns_pattern", ":prod-us-west-2-starport-layer-bucket.s3.us-west-2.amazonaws.com:", who="server"),
            ], changes=[
                ("server", "dns_pattern", ".*:prod-us-west-2-starport-layer-bucket.s3.us-west-2.amazonaws.com:.*"),
            ]),
    ]

print("Adding meta-policies to runner")
api.mpr.add(
        MpDockerd,
)
