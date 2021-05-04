FAQ
===

What is Araali
--------------
Araali transparently wraps any application without requiring any change such
that it is assigned a stable identity via our distributed trust fabric, that
also controls all communication attempts between them.

Our least privilege policies are automatically discovered with a single click
install that requires no config and comes with a do no harm guarantee.

This is particularly useful for cloud native where applications are spun up
dynamically and are often ephemeral. The identity based policies are location
and IP independent, making them reusable post discovery.

MTLS vs Araali
--------------
MTLS is primarily giving you data in flight encryption. The certificates are
tied to infrastructure elements like nodes, IPs and Pods, not to the transport
endpoints. A malware behind the pod enjoys the same privilege. Moreover, there
is also authorization to do once identity is established. Araali makes auto
discovery of least privilege communication policies a breeze and enforces it
too.

Service Mesh vs Araali
----------------------
Service mesh helps with service discovery, load balancing and circuit breaking.
Araali does not offer any of these functions. Service mesh also offers security
policy. However these are at pod/IP level and any malware sitting behind the IP
enjoys the same privilege. Moreover, Araali makes policy discovery a breeze.
These policies are portable and permanent and enjoy the same lifecycle as the
app itself.
