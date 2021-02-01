import api

class MpAwsEks:
    policies = [
        api.AcceptLink(filters=[
                api.f.endpoint("app", "kube-system.kube.kube-proxy"),
                api.f.type("NAE"),
                api.f.endpoint("process", "kube-proxy", who="client"),
                api.f.endpoint("dns_pattern", ":.*\.eks\.amazonaws\.com:", who="server"),
            ], changes=[
                ("server", "dns_pattern", ":.*\.eks\.amazonaws\.com:"),
            ]),
        api.AcceptLink(filters=[
                api.f.endpoint("process", "aws-cni", who="client"),
                api.f.endpoint("process", "aws-k8s-agent", who="server"),
            ], changes=[
            ]),
        api.AcceptLink(filters=[
                api.f.endpoint("process", "aws-k8s-agent", who="client"),
                api.f.endpoint("dns_pattern", ":ec2.us-west-2.amazonaws.com:"),
            ], changes=[
                ("server", "dns_pattern", ":ec2\..*\.amazonaws\.com:"),
            ]),
    ]

print("Adding meta-policies to runner")
api.mpr.add(MpAwsEks)
