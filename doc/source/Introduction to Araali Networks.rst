Introduction to Araali Networks
===============================


What is Araali?
***************

Araali **transparently** secures the **network connections between services** deployed on VM, containers, and container management platforms like Kubernetes. It creates an **identity-based, passwordless system** that performs authentication, authorization, and audits for any inter-service communication out of the box. The identity-based paradigm is critical for modern cloud-native constructs where infrastructure is ephemeral, and security tools cannot use network-based constructs like IPs and Ports.

At its core, Araali leverages eBPF, the superpower of Linux and an identity paradigm inspired by Spiffe-Spire. It provides powerful **visibility and security controls** without any code recompiles/changes, has no performance penalty, and guarantees no packet drops or disruptions. Araali deploys with a single command to covers your fleets of nodes on the Kubernetes clusters or VMs on the cloud.

Visibility
***********

Once deployed, you instantly **see your apps and services as a network diagram** that is easy to understand and discover anomalies. Araali covers inter-cluster traffic, intra-cluster traffic, ingress traffic, and egress going to a particular DNS. 

It also works beautifully for hybrid environments where your Kubernetes cluster might be communicating with a VM or workloads spanning multiple clouds. 

Security
*********

Araali auto-discovers identity-based policies that are reviewed and accepted via APIs or Araali UI. Once these are accepted, you can turn on Alerts to send exact contextual alerts to the app owner. Till this point, Araali is running in monitoring and alert mode.

Once you have monitored your apps for a period, you can **turn on enforcement** with the flip of a switch, and araali can enforce all the policies. Enforcement means only the whitelisted/created policies will be allowed, and everything else will be dropped. Enforcement is an intrusive mode, and we recommend you actively monitor for the initial few days.

We recommend starting your journey from inside out, **focusing on your crown jewels first**. Once enforced it will give you peace of mind that only legitimate processes can talk to the data layer, nothing else.

Key Insights in building Araali
********************************

As the cloud gained prominence, networking got abstracted from the operations teams as they did not own or control the networking boxes anymore. Focus shifted to IAM roles. Furthermore, the networking controls that the cloud providers opened (Security Groups) were **primarily IP and Port-based** and predated the network security stack by over a decade.

Araali’s critical insight was to **decouple security from the infrastructure and create it as an overlay** that could be orchestrated in a distributed fashion. Every node/VM gets its **personal eBPF based firewall** which could enforce Zero Trust security based on Identities. The identity-based policy is auto-discovered to elevate Dev and SecOps team from writing any declarative policies.

eBPF has enabled visibility and control over apps and services at a granularity and efficiency that was not possible before without any recompile or changes. Also, it is well-equipped to handle **modern containerized workloads** as well as more traditional workloads such as **virtual machines and standard Linux processes** till these are running modern Linux kernels that support eBPF.
