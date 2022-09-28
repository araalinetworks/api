# Protocol Documentation
<a name="top"></a>

## Table of Contents

- [araali_api_service.proto](#araali_api_service-proto)
    - [AddUserRequest](#araali_api_service-AddUserRequest)
    - [AlertFilter](#araali_api_service-AlertFilter)
    - [AlertInfo](#araali_api_service-AlertInfo)
    - [AraaliAPIResponse](#araali_api_service-AraaliAPIResponse)
    - [AraaliEndpoint](#araali_api_service-AraaliEndpoint)
    - [AraaliFwKnobs](#araali_api_service-AraaliFwKnobs)
    - [AraaliUser](#araali_api_service-AraaliUser)
    - [Asset](#araali_api_service-Asset)
    - [AssetFilter](#araali_api_service-AssetFilter)
    - [Capabilities](#araali_api_service-Capabilities)
    - [CreateFortifyYamlRequest](#araali_api_service-CreateFortifyYamlRequest)
    - [CreateFortifyYamlResponse](#araali_api_service-CreateFortifyYamlResponse)
    - [CreateTenantRequest](#araali_api_service-CreateTenantRequest)
    - [CreateTenantResponse](#araali_api_service-CreateTenantResponse)
    - [DeleteFortifyYamlRequest](#araali_api_service-DeleteFortifyYamlRequest)
    - [DeleteTenantRequest](#araali_api_service-DeleteTenantRequest)
    - [DeleteUserRequest](#araali_api_service-DeleteUserRequest)
    - [EndPoint](#araali_api_service-EndPoint)
    - [FirewallConfigResponse](#araali_api_service-FirewallConfigResponse)
    - [GetFirewallConfigRequest](#araali_api_service-GetFirewallConfigRequest)
    - [Insight](#araali_api_service-Insight)
    - [Lens](#araali_api_service-Lens)
    - [Link](#araali_api_service-Link)
    - [ListAlertsRequest](#araali_api_service-ListAlertsRequest)
    - [ListAlertsResponse](#araali_api_service-ListAlertsResponse)
    - [ListAssetsRequest](#araali_api_service-ListAssetsRequest)
    - [ListAssetsResponse](#araali_api_service-ListAssetsResponse)
    - [ListFortifyYamlRequest](#araali_api_service-ListFortifyYamlRequest)
    - [ListFortifyYamlResponse](#araali_api_service-ListFortifyYamlResponse)
    - [ListInsightsRequest](#araali_api_service-ListInsightsRequest)
    - [ListInsightsResponse](#araali_api_service-ListInsightsResponse)
    - [ListLinksRequest](#araali_api_service-ListLinksRequest)
    - [ListLinksResponse](#araali_api_service-ListLinksResponse)
    - [ListPolicyAndEnforcementStatusRequest](#araali_api_service-ListPolicyAndEnforcementStatusRequest)
    - [ListPolicyAndEnforcementStatusResponse](#araali_api_service-ListPolicyAndEnforcementStatusResponse)
    - [NonAraaliClientEndpoint](#araali_api_service-NonAraaliClientEndpoint)
    - [NonAraaliEndpoint](#araali_api_service-NonAraaliEndpoint)
    - [NonAraaliServerEndpoint](#araali_api_service-NonAraaliServerEndpoint)
    - [PolicyInfo](#araali_api_service-PolicyInfo)
    - [Ports](#araali_api_service-Ports)
    - [Subnet](#araali_api_service-Subnet)
    - [Tenant](#araali_api_service-Tenant)
    - [TimeSlice](#araali_api_service-TimeSlice)
    - [UpdateFirewallConfigRequest](#araali_api_service-UpdateFirewallConfigRequest)
    - [Vulnerability](#araali_api_service-Vulnerability)
  
    - [AlertInfo.Status](#araali_api_service-AlertInfo-Status)
    - [AraaliAPIResponse.ReturnCode](#araali_api_service-AraaliAPIResponse-ReturnCode)
    - [AraaliUser.Role](#araali_api_service-AraaliUser-Role)
    - [Asset.AssetMode](#araali_api_service-Asset-AssetMode)
    - [Asset.AssetState](#araali_api_service-Asset-AssetState)
    - [Asset.AssetType](#araali_api_service-Asset-AssetType)
    - [FortifyYamlType](#araali_api_service-FortifyYamlType)
    - [Lens.LensType](#araali_api_service-Lens-LensType)
    - [Link.LinkDirection](#araali_api_service-Link-LinkDirection)
    - [LinkState](#araali_api_service-LinkState)
    - [NonAraaliEndpoint.EndpointGroup](#araali_api_service-NonAraaliEndpoint-EndpointGroup)
    - [Vulnerability.Severity](#araali_api_service-Vulnerability-Severity)
  
    - [AraaliAPI](#araali_api_service-AraaliAPI)
  
- [Scalar Value Types](#scalar-value-types)



<a name="araali_api_service-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## araali_api_service.proto



<a name="araali_api_service-AddUserRequest"></a>

### AddUserRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant | [Tenant](#araali_api_service-Tenant) |  | Tenant of the user being added |
| user | [AraaliUser](#araali_api_service-AraaliUser) |  | Information required to create the tenant |






<a name="araali_api_service-AlertFilter"></a>

### AlertFilter
Fields to filter alerts in the ListAlerts API.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| open_alerts | [bool](#bool) |  | Fetch open alerts |
| closed_alerts | [bool](#bool) |  | Fetch closed alerts |
| perimeter_egress | [bool](#bool) |  | Fetch perimeter egress alerts |
| perimeter_ingress | [bool](#bool) |  | Fetch perimeter ingress alerts |
| home_non_araali_egress | [bool](#bool) |  | Fetch non araali egress alerts from private subnets |
| home_non_araali_ingress | [bool](#bool) |  | Fetch non araali ingress alerts from private subnets |
| araali_to_araali | [bool](#bool) |  | Fetch araali to araali alerts |
| list_all_alerts | [bool](#bool) |  | Fetch all alerts from all lenses, even ones not monitored by current user |
| time | [TimeSlice](#araali_api_service-TimeSlice) |  | Time range in which to fetch alerts |
| zone | [string](#string) |  | Fetch alerts for given zone |






<a name="araali_api_service-AlertInfo"></a>

### AlertInfo
Additional information about alerts


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| communication_alert_type | [string](#string) |  | Alert type |
| process_alert_type | [string](#string) |  | Process alert type |
| re_open_count | [uint32](#uint32) |  | Number of times transitioned from SNOOZED -&gt; ALERT |
| status | [AlertInfo.Status](#araali_api_service-AlertInfo-Status) |  | Whether OPEN or CLOSED |






<a name="araali_api_service-AraaliAPIResponse"></a>

### AraaliAPIResponse
Generic API response object.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| code | [AraaliAPIResponse.ReturnCode](#araali_api_service-AraaliAPIResponse-ReturnCode) |  | Success/Failure of API call |
| message | [string](#string) |  | Custom message returned by the service if any |






<a name="araali_api_service-AraaliEndpoint"></a>

### AraaliEndpoint
Represents an araali endpoint


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| zone | [string](#string) |  | Zone the endpoint belongs to |
| app | [string](#string) |  | Mapped app the endpoint belongs to |
| unmapped_app | [string](#string) |  | Original app/namespace the endpoint belongs to |
| namespace | [string](#string) |  | Namespace of the endpoint |
| pod | [string](#string) |  | Pod the endpoint belongs to |
| container_name | [string](#string) |  | Container the endpoint belongs to |
| process | [string](#string) |  | Process of the endpoint belongs to |
| binary_name | [string](#string) |  | Binary name of the endpoint process |
| parent_process | [string](#string) |  | Parent of the endpoint process |






<a name="araali_api_service-AraaliFwKnobs"></a>

### AraaliFwKnobs



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| install | [bool](#bool) |  |  |
| enable_process_vulnerabilities | [bool](#bool) |  |  |
| enable_container_vulnerabilities | [bool](#bool) |  |  |
| enable_flow_dedup | [bool](#bool) |  |  |
| enable_flow_rate_limit | [bool](#bool) |  |  |






<a name="araali_api_service-AraaliUser"></a>

### AraaliUser
User object identifying the user in API calls.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| email | [string](#string) |  | E-mail of the registering user |
| role | [AraaliUser.Role](#araali_api_service-AraaliUser-Role) |  | Role of the registering user |
| is_site_admin | [bool](#bool) |  | Enables role to have access to zone-apps 		TRUE - Enable modify access to zone-apps 		FALSE - Enable read-only access to zone-apps. |






<a name="araali_api_service-Asset"></a>

### Asset
Representation of container/virtual machine information.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| host_name | [string](#string) |  | Host name of asset |
| ip_address | [string](#string) |  | IP address assigned to the asset |
| uuid | [string](#string) |  | UUID if virtual machine or container-id if container |
| image | [string](#string) |  | Container image or ami-id for virtual machines |
| zone | [string](#string) |  | Zone the asset belongs to |
| apps | [string](#string) | repeated | Apps the asset belongs to |
| state | [Asset.AssetState](#araali_api_service-Asset-AssetState) |  | State of the asset active, inactive etc |
| asset_type | [Asset.AssetType](#araali_api_service-Asset-AssetType) |  | Type of the asset |
| vulnerabilities | [Vulnerability](#araali_api_service-Vulnerability) | repeated | Vulnerabilities in the asset |
| mode | [Asset.AssetMode](#araali_api_service-Asset-AssetMode) |  | Visibility/Enforcement mode of the asset |
| os_name | [string](#string) |  | OS name of the asset |
| iam_role | [string](#string) |  | AWS IAM Role assigned to the asset |
| docker_privileged | [bool](#bool) |  | Docker privilege assigned to the container (Docker containers only) |
| docker | [Capabilities](#araali_api_service-Capabilities) |  | Capabilities exported by docker |
| containerd | [Capabilities](#araali_api_service-Capabilities) |  | Capabilities exported by containerd |






<a name="araali_api_service-AssetFilter"></a>

### AssetFilter
Flags to filter assets in the ListAssets API.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| list_active_vm | [bool](#bool) |  | Return active virtual machines |
| list_inactive_vm | [bool](#bool) |  | Return inactive virtual machines |
| list_active_container | [bool](#bool) |  | Return active containers |
| list_inactive_container | [bool](#bool) |  | Return inactive containers |






<a name="araali_api_service-Capabilities"></a>

### Capabilities
List of capabilities


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| capabilities | [string](#string) | repeated |  |






<a name="araali_api_service-CreateFortifyYamlRequest"></a>

### CreateFortifyYamlRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant | [Tenant](#araali_api_service-Tenant) |  | Handle of tenant |
| workload_name | [string](#string) |  | Workload name - Unique name associated with workload. This is also the zone name - Cluster would show up on UI/Araali interfaces with this name |
| fog | [string](#string) |  | DNS of Fog that communicates with the cluster (Optional, take defaults if empty) |
| disable_upgrade | [bool](#bool) |  | Disable upgrade (Optional - false by default) |
| disable_enforcement | [bool](#bool) |  | Disable enforcement (Optional - false by default) |
| yaml_type | [FortifyYamlType](#araali_api_service-FortifyYamlType) |  | Type of yaml file to generate |






<a name="araali_api_service-CreateFortifyYamlResponse"></a>

### CreateFortifyYamlResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| response | [AraaliAPIResponse](#araali_api_service-AraaliAPIResponse) |  | CreateFortifyYamlResponse API call response |
| workload_yaml | [string](#string) |  | Yaml formatted string response |






<a name="araali_api_service-CreateTenantRequest"></a>

### CreateTenantRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant | [Tenant](#araali_api_service-Tenant) |  | Information required to create the tenant |






<a name="araali_api_service-CreateTenantResponse"></a>

### CreateTenantResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| response | [AraaliAPIResponse](#araali_api_service-AraaliAPIResponse) |  | Success/Failure of the API call |
| tenant | [Tenant](#araali_api_service-Tenant) |  | Handle for the newly created tenant |






<a name="araali_api_service-DeleteFortifyYamlRequest"></a>

### DeleteFortifyYamlRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant | [Tenant](#araali_api_service-Tenant) |  | Handle of tenant |
| workload_name | [string](#string) |  | Unique ID associated with cluster |






<a name="araali_api_service-DeleteTenantRequest"></a>

### DeleteTenantRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant | [Tenant](#araali_api_service-Tenant) |  | Tenant being deleted |






<a name="araali_api_service-DeleteUserRequest"></a>

### DeleteUserRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant | [Tenant](#araali_api_service-Tenant) |  | Tenant of the user being deleted |
| user | [AraaliUser](#araali_api_service-AraaliUser) |  | Handle of the user being deleted |






<a name="araali_api_service-EndPoint"></a>

### EndPoint
Represents one end of a link/alert_counts


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| araali | [AraaliEndpoint](#araali_api_service-AraaliEndpoint) |  | Araali endpoint info |
| non_araali | [NonAraaliEndpoint](#araali_api_service-NonAraaliEndpoint) |  | Non-Araali endpoint info |






<a name="araali_api_service-FirewallConfigResponse"></a>

### FirewallConfigResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant_id | [string](#string) |  |  |
| zone | [string](#string) |  |  |
| knobs | [AraaliFwKnobs](#araali_api_service-AraaliFwKnobs) |  |  |






<a name="araali_api_service-GetFirewallConfigRequest"></a>

### GetFirewallConfigRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant_id | [string](#string) |  |  |
| zone | [string](#string) |  |  |






<a name="araali_api_service-Insight"></a>

### Insight
Instance of the insight Representation


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| reason | [string](#string) |  | The kind of insight captured |
| url | [string](#string) |  | The URL to view the insights |
| count | [uint32](#uint32) |  | Number of insights |
| lens | [Lens](#araali_api_service-Lens) | repeated | The zone/app the insights belong to |






<a name="araali_api_service-Lens"></a>

### Lens
Drilled down entity/lens


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| type | [Lens.LensType](#araali_api_service-Lens-LensType) |  | Lens type |
| zone | [string](#string) |  | Zone of the lens |
| app | [string](#string) |  | App lens |
| pod | [string](#string) |  | Pod of the lens |
| container_name | [string](#string) |  | Container of the lens |
| process | [string](#string) |  | Process of the lens |
| parent_process | [string](#string) |  | Parent process of the lens |
| binary_name | [string](#string) |  | Binary name of the lens |
| service | [string](#string) |  | Service lens |






<a name="araali_api_service-Link"></a>

### Link
Represents an alert or policy link


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| client | [EndPoint](#araali_api_service-EndPoint) |  | Client endpoint |
| server | [EndPoint](#araali_api_service-EndPoint) |  | Server endpoint |
| direction | [Link.LinkDirection](#araali_api_service-Link-LinkDirection) |  | Direction of client-server link |
| timestamp | [google.protobuf.Timestamp](#google-protobuf-Timestamp) |  | Timestamp when link was discovered |
| unique_id | [string](#string) |  | Unique handle to the link |
| state | [LinkState](#araali_api_service-LinkState) |  | State of the link alert, active/snoozed etc |
| ports | [Ports](#araali_api_service-Ports) |  | Aggregated active/inactive ports |
| alert_info | [AlertInfo](#araali_api_service-AlertInfo) |  | Additional information for alerts |
| policy_info | [PolicyInfo](#araali_api_service-PolicyInfo) |  | Additional information for policy links |






<a name="araali_api_service-ListAlertsRequest"></a>

### ListAlertsRequest
Request for alerts received by tenant


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant | [Tenant](#araali_api_service-Tenant) |  | Handle to tenant |
| filter | [AlertFilter](#araali_api_service-AlertFilter) |  | Filter responses |
| count | [int32](#int32) |  | Number of alerts to be returned each API call |
| paging_token | [string](#string) |  | Token to be sent in the next API call to retrieve the next set of alerts (paging) |






<a name="araali_api_service-ListAlertsResponse"></a>

### ListAlertsResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| response | [AraaliAPIResponse](#araali_api_service-AraaliAPIResponse) |  | ListAsset API call response |
| links | [Link](#araali_api_service-Link) | repeated | List of alerts |
| paging_token | [string](#string) |  | Token to be passed to the next API call (indicating there are more alerts to be retrieved) |






<a name="araali_api_service-ListAssetsRequest"></a>

### ListAssetsRequest
Request for the list of assets (virtual machines/containers) in a tenant.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant | [Tenant](#araali_api_service-Tenant) |  | Handle of the tenant |
| zone | [string](#string) |  | Zone from which to return assets |
| app | [string](#string) |  | App/Namespace from which to return assets |
| time | [TimeSlice](#araali_api_service-TimeSlice) |  | Start/End time range from which to return assets |
| filter | [AssetFilter](#araali_api_service-AssetFilter) |  | Filter assets based on type and active/inactive |






<a name="araali_api_service-ListAssetsResponse"></a>

### ListAssetsResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| response | [AraaliAPIResponse](#araali_api_service-AraaliAPIResponse) |  | ListAsset API call response |
| assets | [Asset](#araali_api_service-Asset) | repeated | List of assets |






<a name="araali_api_service-ListFortifyYamlRequest"></a>

### ListFortifyYamlRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant | [Tenant](#araali_api_service-Tenant) |  | Handle of tenant |
| yaml_type | [FortifyYamlType](#araali_api_service-FortifyYamlType) |  | Type of yaml to list |






<a name="araali_api_service-ListFortifyYamlResponse"></a>

### ListFortifyYamlResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| response | [AraaliAPIResponse](#araali_api_service-AraaliAPIResponse) |  | ListWorkloadResponse API call response |
| workloads | [string](#string) | repeated | List of workloads |






<a name="araali_api_service-ListInsightsRequest"></a>

### ListInsightsRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant | [Tenant](#araali_api_service-Tenant) |  | Handle of tenant |
| zone | [string](#string) |  | Zone where insights are requested |






<a name="araali_api_service-ListInsightsResponse"></a>

### ListInsightsResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| response | [AraaliAPIResponse](#araali_api_service-AraaliAPIResponse) |  | ListInsights API call response |
| insights | [Insight](#araali_api_service-Insight) | repeated | List of insights |






<a name="araali_api_service-ListLinksRequest"></a>

### ListLinksRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant | [Tenant](#araali_api_service-Tenant) |  | Handle for the tenant |
| zone | [string](#string) |  | Zone for the request |
| app | [string](#string) |  | App for the request |
| service | [string](#string) |  | Required when zone and app are not specified. Must be in form of ip:port or fqdn:port |
| time | [TimeSlice](#araali_api_service-TimeSlice) |  | Time range for the list links request |






<a name="araali_api_service-ListLinksResponse"></a>

### ListLinksResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| response | [AraaliAPIResponse](#araali_api_service-AraaliAPIResponse) |  | ListLinks API call response |
| links | [Link](#araali_api_service-Link) | repeated | List of links |






<a name="araali_api_service-ListPolicyAndEnforcementStatusRequest"></a>

### ListPolicyAndEnforcementStatusRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant | [Tenant](#araali_api_service-Tenant) |  | Handle of tenant |
| zone | [string](#string) |  | Zone to which container belongs |
| app | [string](#string) |  | App to which container belongs |
| pod | [string](#string) |  | Pod to which container belongs |
| container | [string](#string) |  | container name |






<a name="araali_api_service-ListPolicyAndEnforcementStatusResponse"></a>

### ListPolicyAndEnforcementStatusResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| policy_and_enforcement_yaml | [string](#string) |  | Policies represented in yaml format. |






<a name="araali_api_service-NonAraaliClientEndpoint"></a>

### NonAraaliClientEndpoint
Represents a non araali client endpoint


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| subnet | [Subnet](#araali_api_service-Subnet) |  | Client subnet |






<a name="araali_api_service-NonAraaliEndpoint"></a>

### NonAraaliEndpoint
Represents a non araali endpoint


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| client | [NonAraaliClientEndpoint](#araali_api_service-NonAraaliClientEndpoint) |  | Non araali client |
| server | [NonAraaliServerEndpoint](#araali_api_service-NonAraaliServerEndpoint) |  | Non araali server |
| endpoint_group | [NonAraaliEndpoint.EndpointGroup](#araali_api_service-NonAraaliEndpoint-EndpointGroup) |  | WORLD if public subnet. HOME if private subnet. |
| organization | [string](#string) |  | Autonomous System Organization of the IP address if available |






<a name="araali_api_service-NonAraaliServerEndpoint"></a>

### NonAraaliServerEndpoint
Represents a non araali server endpoint


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| dns_pattern | [string](#string) |  | DNS/FQDN of endpoint |
| subnet | [Subnet](#araali_api_service-Subnet) |  | Server subnet |
| dst_port | [uint32](#uint32) |  | Service destination port |






<a name="araali_api_service-PolicyInfo"></a>

### PolicyInfo
Additional information about policy


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| template_name | [string](#string) |  | Template name used to validate the link |
| template_user | [string](#string) |  | User who created the template to validate the link |
| policy_skip_reason | [string](#string) |  | Reason for skipping policy evaluation at agents when enforced |






<a name="araali_api_service-Ports"></a>

### Ports



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| active_ports | [uint32](#uint32) | repeated | Active aggregated ports in the link |
| inactive_ports | [uint32](#uint32) | repeated | Inactive aggregated ports in the link |






<a name="araali_api_service-Subnet"></a>

### Subnet
Represents the subnet/mask


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| subnet | [string](#string) |  | Client subnet |
| net_mask | [uint32](#uint32) |  | Client netmask |






<a name="araali_api_service-Tenant"></a>

### Tenant
Tenant object identifying the tenant in API calls.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| id | [string](#string) |  | Id of the tenant |
| admin_email | [string](#string) |  | Admin e-mail of the tenant. Also adds an ADMIN role user in this tenant. |






<a name="araali_api_service-TimeSlice"></a>

### TimeSlice
Object for specifying start and end time in varous API calls.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| start_time | [google.protobuf.Timestamp](#google-protobuf-Timestamp) |  | Start time to fetch from. Specify 0 to indicate beginning of time |
| end_time | [google.protobuf.Timestamp](#google-protobuf-Timestamp) |  | End time to fetch up to |






<a name="araali_api_service-UpdateFirewallConfigRequest"></a>

### UpdateFirewallConfigRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| tenant_id | [string](#string) |  |  |
| zone | [string](#string) |  |  |
| knobs | [AraaliFwKnobs](#araali_api_service-AraaliFwKnobs) |  |  |






<a name="araali_api_service-Vulnerability"></a>

### Vulnerability
Captures an instance of vulnerability package name, cve info etc


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| package_name | [string](#string) |  | Package name with the vulnerability |
| cve_id | [string](#string) | repeated | CVE id of the vulnerability |
| severity | [Vulnerability.Severity](#araali_api_service-Vulnerability-Severity) |  | Severity of the vulnerability |





 


<a name="araali_api_service-AlertInfo-Status"></a>

### AlertInfo.Status


| Name | Number | Description |
| ---- | ------ | ----------- |
| UNKNOWN_STATUS | 0 |  |
| OPEN | 1 |  |
| CLOSED | 2 |  |



<a name="araali_api_service-AraaliAPIResponse-ReturnCode"></a>

### AraaliAPIResponse.ReturnCode
Return status codes for the Araali APIs

| Name | Number | Description |
| ---- | ------ | ----------- |
| SUCCESS | 0 | API call succeeded |
| FAILURE | 1 | API call failed |
| UNKNOWN | 2 | Status unknown (Should never happen) |



<a name="araali_api_service-AraaliUser-Role"></a>

### AraaliUser.Role
Enum for specifying the role of a user

| Name | Number | Description |
| ---- | ------ | ----------- |
| ADMIN | 0 | Enables user to create, modify other users |
| USER | 1 | Set if the user is not an administrator |



<a name="araali_api_service-Asset-AssetMode"></a>

### Asset.AssetMode
Mode the asset is in
		TAP    - Tap&#39;s into telemetry to discover policies (no enforcement).
		INLINE - Firewall embedded inline to enforce policies if needed (enforcement).

| Name | Number | Description |
| ---- | ------ | ----------- |
| TAP | 0 | No enforcement/visibility mode |
| INLINE | 1 | Inline enforcement mode |
| TRANSITIONING_TAP_TO_INLINE | 2 | Transitioning from TAP to INLINE |
| TRANSITIONING_INLINE_TO_TAP | 3 | Transitioning from INLINE to TAP |



<a name="araali_api_service-Asset-AssetState"></a>

### Asset.AssetState
State of the asset

| Name | Number | Description |
| ---- | ------ | ----------- |
| DELETED | 0 | Asset has been deleted |
| ACTIVE | 1 | Asset is active |
| INACTIVE | 2 | Asset is inactive |



<a name="araali_api_service-Asset-AssetType"></a>

### Asset.AssetType
Type of the asset

| Name | Number | Description |
| ---- | ------ | ----------- |
| UNKNOWN_ASSET | 0 | Unknown asset type |
| VIRTUAL_MACHINE | 1 | Virtual Machine type |
| CONTAINER | 2 | Container type |



<a name="araali_api_service-FortifyYamlType"></a>

### FortifyYamlType


| Name | Number | Description |
| ---- | ------ | ----------- |
| UNKNOWN | 0 | Unknown |
| HELM_VALUES_FILE | 1 | Generate helm values file for helm chart based approach |



<a name="araali_api_service-Lens-LensType"></a>

### Lens.LensType
Type of lens

| Name | Number | Description |
| ---- | ------ | ----------- |
| UNKNOWN_LENS | 0 | Unspecified |
| ZONE_APP | 1 | Zone/App level |
| SERVICE | 2 | Service level |
| ZONE | 3 | Zone level |
| PROCESS | 4 | Process level |
| CONTAINER | 5 | Container level |
| TENANT | 6 | Tenant level |



<a name="araali_api_service-Link-LinkDirection"></a>

### Link.LinkDirection
Direction of the link araali-araali, araali-ingress etc

| Name | Number | Description |
| ---- | ------ | ----------- |
| UNKNOWN_DIRECTION | 0 | Unknown |
| NON_ARAALI_INGRESS | 1 | Ingress from an unprotected non-araali endpoint |
| ARAALI_INGRESS | 2 | Ingress from an araali protected endpoint |
| NON_ARAALI_EGRESS | 3 | Egress to an unprotected non-araali endpoint |
| ARAALI_EGRESS | 4 | Egress to an araali protected endpoint |
| INTERNAL | 5 | Link between two araali endpoints within an app |



<a name="araali_api_service-LinkState"></a>

### LinkState
Type of a link Alert or PolicyInfo

| Name | Number | Description |
| ---- | ------ | ----------- |
| BASELINE_ALERT | 0 | Alert |
| DEFINED_POLICY | 1 | Currently active policy |
| SNOOZED_POLICY | 2 | Policy that was discovered but removed/snoozed |
| DENIED_POLICY | 3 | Deny policy |



<a name="araali_api_service-NonAraaliEndpoint-EndpointGroup"></a>

### NonAraaliEndpoint.EndpointGroup


| Name | Number | Description |
| ---- | ------ | ----------- |
| UNKNOWN_GROUP | 0 |  |
| WORLD | 1 |  |
| HOME | 2 |  |



<a name="araali_api_service-Vulnerability-Severity"></a>

### Vulnerability.Severity


| Name | Number | Description |
| ---- | ------ | ----------- |
| NONE | 0 | No severity |
| LOW | 1 | Low severity |
| MEDIUM | 2 | Medium severity |
| HIGH | 3 | High severity |
| CRITICAL | 4 | Critical severity |


 

 


<a name="araali_api_service-AraaliAPI"></a>

### AraaliAPI


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| createTenant | [CreateTenantRequest](#araali_api_service-CreateTenantRequest) | [CreateTenantResponse](#araali_api_service-CreateTenantResponse) | Add a tenant |
| deleteTenant | [DeleteTenantRequest](#araali_api_service-DeleteTenantRequest) | [AraaliAPIResponse](#araali_api_service-AraaliAPIResponse) | Delete a tenant |
| addUser | [AddUserRequest](#araali_api_service-AddUserRequest) | [AraaliAPIResponse](#araali_api_service-AraaliAPIResponse) | Add a user |
| deleteUser | [DeleteUserRequest](#araali_api_service-DeleteUserRequest) | [AraaliAPIResponse](#araali_api_service-AraaliAPIResponse) | Delete a user |
| listAssets | [ListAssetsRequest](#araali_api_service-ListAssetsRequest) | [ListAssetsResponse](#araali_api_service-ListAssetsResponse) | Get assets |
| listAlerts | [ListAlertsRequest](#araali_api_service-ListAlertsRequest) | [ListAlertsResponse](#araali_api_service-ListAlertsResponse) | Get alerts |
| listLinks | [ListLinksRequest](#araali_api_service-ListLinksRequest) | [ListLinksResponse](#araali_api_service-ListLinksResponse) | Get links within a zone/app |
| listInsights | [ListInsightsRequest](#araali_api_service-ListInsightsRequest) | [ListInsightsResponse](#araali_api_service-ListInsightsResponse) | Get tenant wide insights |
| createFortifyYaml | [CreateFortifyYamlRequest](#araali_api_service-CreateFortifyYamlRequest) | [CreateFortifyYamlResponse](#araali_api_service-CreateFortifyYamlResponse) | Generate k8s workload/helm values (also registers workloadID) |
| listFortifyYaml | [ListFortifyYamlRequest](#araali_api_service-ListFortifyYamlRequest) | [ListFortifyYamlResponse](#araali_api_service-ListFortifyYamlResponse) | List existing k8s workloads |
| deleteFortifyYaml | [DeleteFortifyYamlRequest](#araali_api_service-DeleteFortifyYamlRequest) | [AraaliAPIResponse](#araali_api_service-AraaliAPIResponse) | Delete existing k8s workload |
| listPolicyAndEnforcementStatus | [ListPolicyAndEnforcementStatusRequest](#araali_api_service-ListPolicyAndEnforcementStatusRequest) | [ListPolicyAndEnforcementStatusResponse](#araali_api_service-ListPolicyAndEnforcementStatusResponse) | Download policy and enforcement knobs as code. |
| getFirewallConfig | [GetFirewallConfigRequest](#araali_api_service-GetFirewallConfigRequest) | [FirewallConfigResponse](#araali_api_service-FirewallConfigResponse) | Get existing Araali firewall config |
| updateFirewallConfig | [UpdateFirewallConfigRequest](#araali_api_service-UpdateFirewallConfigRequest) | [FirewallConfigResponse](#araali_api_service-FirewallConfigResponse) | Update existing Araali firewall config |

 



## Scalar Value Types

| .proto Type | Notes | C++ | Java | Python | Go | C# | PHP | Ruby |
| ----------- | ----- | --- | ---- | ------ | -- | -- | --- | ---- |
| <a name="double" /> double |  | double | double | float | float64 | double | float | Float |
| <a name="float" /> float |  | float | float | float | float32 | float | float | Float |
| <a name="int32" /> int32 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint32 instead. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="int64" /> int64 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint64 instead. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="uint32" /> uint32 | Uses variable-length encoding. | uint32 | int | int/long | uint32 | uint | integer | Bignum or Fixnum (as required) |
| <a name="uint64" /> uint64 | Uses variable-length encoding. | uint64 | long | int/long | uint64 | ulong | integer/string | Bignum or Fixnum (as required) |
| <a name="sint32" /> sint32 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int32s. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="sint64" /> sint64 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int64s. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="fixed32" /> fixed32 | Always four bytes. More efficient than uint32 if values are often greater than 2^28. | uint32 | int | int | uint32 | uint | integer | Bignum or Fixnum (as required) |
| <a name="fixed64" /> fixed64 | Always eight bytes. More efficient than uint64 if values are often greater than 2^56. | uint64 | long | int/long | uint64 | ulong | integer/string | Bignum |
| <a name="sfixed32" /> sfixed32 | Always four bytes. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="sfixed64" /> sfixed64 | Always eight bytes. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="bool" /> bool |  | bool | boolean | boolean | bool | bool | boolean | TrueClass/FalseClass |
| <a name="string" /> string | A string must always contain UTF-8 encoded or 7-bit ASCII text. | string | String | str/unicode | string | string | string | String (UTF-8) |
| <a name="bytes" /> bytes | May contain any arbitrary sequence of bytes. | string | ByteString | str | []byte | ByteString | string | String (ASCII-8BIT) |

