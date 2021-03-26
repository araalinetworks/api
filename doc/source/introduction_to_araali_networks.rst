Introduction to Araali Networks
===============================


What is Araali?
***************

Araali **transparently** secures the **network connections between services**
deployed on VMs, containers, and container management platforms like
Kubernetes. It creates an **identity-based, passwordless system** that
performs authentication, authorization, and audit for any inter-service
communication out of the box. The identity-based paradigm is critical for
modern cloud-native constructs where infrastructure is ephemeral, and security
tools cannot use network-based constructs like IPs and ports.

At its core, Araali leverages `eBPF
<https://thenewstack.io/linux-technology-for-the-new-year-ebpf/>`_, the
superpower of Linux and an identity paradigm inspired by `SPIFFE/SPIRE
<https://github.com/spiffe/spire>`_. It provides powerful **visibility and
security controls** without any code recompiles/changes, has no performance
penalty, and guarantees no disruptions by virtue of staying out of the packet
forwarding path. Araali deploys with a single command to cover your fleet of
nodes on the Kubernetes cluster(s) or VMs across clouds.

Visibility
***********

Once deployed, you instantly **see your apps and services as a network
diagram** that is easy to understand and to discover anomalies. Araali covers
inter-cluster traffic, intra-cluster traffic, ingress traffic, and egress
traffic based on DNS in use (if any). 

It also works beautifully for hybrid environments where your Kubernetes cluster
might be communicating with databases on VMs or workloads spanning multiple
clouds and on-prem.

Security
*********

Araali auto-discovers identity-centric policies that are then reviewed and
accepted via APIs or by using the Araali UI. Once these are accepted, you can
turn on alerts that carry the appropriate context and are intelligently
dispatched to the right app owner. Until this point, Araali is running in the
no-harm monitoring and alert mode.

Once you have monitored your apps for a period, you can **turn on enforcement**
with the flip of a switch, and araali can enforce all the policies. Enforcement
means that only the whitelisted/accepted policies will be allowed, and
everything else will be dropped. Enforcement is an intrusive mode, and we
recommend you actively monitor for no alerts for a few days.

We recommend starting your journey inside out, **focusing on your crown jewels
first**. Once enforced, it will give you peace of mind that only legitimate
processes can talk to the data layer, and nothing else. You should then slowly
expand in concentric circles and build depth into your defense.

Key Insights in building Araali
********************************

As the cloud gained prominence, networking got abstracted from the operations
teams as they did not own or control the networking boxes anymore. Focus
shifted to IAM roles. Furthermore, the networking controls that the cloud
providers offered (Security Groups) were **primarily IP and port-based** and
predated the network security stack by over a decade.

Araali’s critical insight was to **decouple security from the infrastructure
and create it as an overlay** that could be orchestrated in a distributed
fashion. Every node/VM gets its **personal eBPF based firewall** which could
enforce Zero Trust security based on Identities. The identity-based policy is
auto-discovered to free Dev and SecOps team from having to handwrite
declarative policies.

eBPF has enabled visibility and control over apps and services at a granularity
and efficiency that was not possible before without any recompile or rewrite.
Also, it is well-equipped to handle **modern containerized workloads** as well
as more traditional workloads such as **virtual machines and standard Linux
processes** as long as these are running modern Linux kernels that support
eBPF.
