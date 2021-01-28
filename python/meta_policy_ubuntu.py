import api

class MpMotd:
    policies = [
        api.AcceptLink(filters=[
                api.f.endpoint("parent_process", "50-motd-news", who="client"),
                api.f.endpoint("dns_pattern", ":motd.ubuntu.com:"),
            ], changes=[
            ]),
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("process", "/usr/lib/ubuntu-release-upgrader/check-new-release", who="client"),
                api.f.endpoint("dns_pattern", [":changelogs.ubuntu.com:"], who="server"),
            ], changes=[
            ]),
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("parent_process", "apt-get", who="client"),
                api.f.endpoint("dns_pattern", [":us-west-2.ec2.archive.ubuntu.com:",
                                           ":downloads.apache.org:",
                                           ":www.apache.org:",
                                           ":security.ubuntu.com:",
                                           ":dl.bintray.com:"], who="server"),
            ], changes=[
            ]),
    ]

print("Adding meta-policies to runner")
api.mpr.add(
        MpMotd,
)
