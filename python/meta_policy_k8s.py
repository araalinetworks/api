import api

class MpK8s:
    policies = [
        api.AcceptLink(filters=[
                api.f.type("INT"),
                api.f.endpoint("app", "monitoring.prometheus.prometheus", who="client"),
                api.f.endpoint("process", "prometheus", who="client"),
                api.f.endpoint("app", "monitoring.grafana.grafana", who="server"),
                api.f.endpoint("process", "grafana-server", who="server"),
            ], changes=[
            ]),
        api.AcceptLink(filters=[
                api.f.type(["AEG", "AIN"]),
                api.f.same_zone,
                api.f.endpoint("app", ["k8s", "monitoring.alertmanager.alertmanager"], who="client"),
                api.f.endpoint("process", ["kubelet", "alertmanager"], who="client"),
                api.f.endpoint("app", "kube-system.coredns.coredns", who="server"),
                api.f.endpoint("process", "coredns", who="server"),
            ], changes=[
            ]),
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("process", "pilot-agent", who="client"),
                api.f.endpoint("subnet", "169.254.169.254", who="server"),
                api.f.endpoint("netmask", 32, who="server"),
                api.f.endpoint("dst_port", 80, who="server"),
            ], changes=[
            ]),
        api.AcceptLink(filters=[
                api.f.type("NAE"),
                api.f.endpoint("app", "kube-system.certmanageraddon-cert-manager.cert-manager"),
                api.f.endpoint("process", "controller", who="client"),
                api.f.endpoint("subnet", "169.254.169.254", who="server"),
                api.f.endpoint("netmask", 32, who="server"),
                api.f.endpoint("dst_port", 80, who="server"),
            ], changes=[
            ]),
    ]

class MpAlertMgr:
    policies = [
        api.AcceptLink(filters=[
                api.f.type("INT"),
                api.f.endpoint("process", "alertmanager", who="client"),
                api.f.endpoint("process", "alertmanager", who="server"),
            ], changes=[
            ]),
    ]

class MpKubeletClient:
    policies = [
        api.AcceptLink(filters=[
                api.f.same_zone,
                api.f.endpoint("process", "kubelet", who="client"),
                api.f.endpoint("process", ["alertmanager", "grafana-server", "prometheus"], who="server"),
            ], changes=[
            ]),
        api.AcceptLink(filters=[
                api.f.type(["AEG", "AIN"]),
                api.f.same_zone,
                api.f.endpoint("app", "k8s", who="client"),
                api.f.endpoint("process", "socat", who="client"),
                api.f.endpoint("app", "monitoring.grafana.grafana", who="server"),
                api.f.endpoint("process", "grafana-server", who="server"),
            ], changes=[
            ]),
    ]

class MpPrometheus:
    policies = [
        api.AcceptLink(filters=[
                api.f.same_zone,
                api.f.endpoint("process", "prometheus", who="client"),
                api.f.endpoint("process", ["alertmanager", "node_exporter", "prometheus", "kubelet", "kube-rbac-proxy",], who="server"),
            ], changes=[
            ]),
    ]


print("Adding meta-policies to runner")
api.mpr.add(MpK8s, MpAlertMgr, MpKubeletClient, MpPrometheus)
