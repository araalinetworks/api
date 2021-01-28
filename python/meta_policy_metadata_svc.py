import api

class MpToMetadataSvc:
    policies = [
        api.AcceptLink(filters=[
                api.f.endpoint("process", ["kubelet",
                                        "aws-iam-authenticator",
                                        "aws-k8s-agent",
                                        "/usr/bin/yum"], who="client"),
                api.f.endpoint("subnet", "169.254.169.254", who="server"),
            ], changes=[
            ]),
    ]

print("Adding meta-policies to runner")
api.mpr.add(
        MpToMetadataSvc,
)
