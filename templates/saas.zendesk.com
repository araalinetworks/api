identities:
- node:
    name: node_0
    zone: .*
    app: .*
    pod: .*
    container: .*
    binary_name: .*
    parent_process: .*
    process: .*
  pushdown: {}
- node:
    name: node_1
    dns_pattern: .*.zendesk.com
    dst_port: 443
  pushdown: {}
authorizations:
- name: node_1
  in:
  - node_0
