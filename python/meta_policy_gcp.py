import api

class MpGCP:
    policies = [
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("process", "dockerd", who="client"),
                api.f.endpoint("dns_pattern", ":storage.googleapis.com:", who="server"),
            ], changes=[
                ("server", "dns_pattern", ".*:storage\.googleapis\.com:.*"),
            ]),
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("process", "/google-cloud-sdk/lib/gcloud.py", who="client"),
                api.f.endpoint("dns_pattern", ":.*.googleapis.com:", who="server"),
            ], changes=[
                ("server", "dns_pattern", ":.*\.googleapis\.com:"),
            ]),
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("process", ["signalfx-agent", "/usr/bin/google_accounts_daemon", "/usr/bin/google_clock_skew_daemon", "/usr/bin/google_network_daemon", "/usr/bin/google_metadata_script_runner"], who="client"),
                api.f.endpoint("subnet", "169.254.169.254", who="server"),
                api.f.endpoint("netmask", 32, who="server"),
                api.f.endpoint("dst_port", 80, who="server"),
            ], changes=[
            ]),
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("process", "google-cloud-sdk/lib/gcloud.py", who="client"),
                api.f.endpoint("dns_pattern", ":metadata.google.internal:", who="server"),
            ], changes=[
                ("server", "dns_pattern", ":metadata\.google\.internal:"),
            ]),
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("app", ".*.istio-proxy"),
                api.f.endpoint("process", "pilot-agent", who="client"),
                api.f.endpoint("dns_pattern", ":metadata.google.internal:", who="server"),
            ], changes=[
                ("server", "dns_pattern", ":metadata\.google\.internal:"),
            ]),   
       api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("app", "linux"),
                api.f.endpoint("process", "/usr/bin/google_", who="client"),
                api.f.endpoint("dns_pattern", ":metadata.google.internal:", who="server"),
            ], changes=[
                ("server", "dns_pattern", ":metadata\.google\.internal:"),
            ]),
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("binary_name", "kubernetes/bin/node-problem-detector", who="client"),
                api.f.endpoint("dns_pattern", ":.*.googleapis.com:", who="server"),
            ], changes=[
                ("server", "dns_pattern", ":.*\.googleapis\.com:"),
            ]),     
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("app", "kube-system\."),
                api.f.endpoint("process", "external-dns", who="client"),            
                api.f.endpoint("dns_pattern", ":.*.googleapis.com:", who="server"),
            ], changes=[
                ("server", "dns_pattern", ":.*\.googleapis\.com:"),
            ]),    
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("app", "kube-system.*.external-dns"),
                api.f.endpoint("process", "external-dns", who="client"),
                api.f.endpoint("dns_pattern", ":metadata.google.internal:", who="server"),
            ], changes=[
                ("server", "dns_pattern", ":metadata\.google\.internal:"),
            ]),           
    ]
    
print("Adding meta-policies to runner")
api.mpr.add(MpGCP)  
