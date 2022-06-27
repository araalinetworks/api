Golang API V2
=============

.. _title:

Golang API V2
=============

Table of Contents
-----------------

.. container::
   :name: toc-container

   -  `araali_api_service.proto <#araali_api_service.proto>`__

      -  `MAddUserRequest <#araali_api_service.AddUserRequest>`__
      -  `MAlertFilter <#araali_api_service.AlertFilter>`__
      -  `MAlertInfo <#araali_api_service.AlertInfo>`__
      -  `MAraaliAPIResponse <#araali_api_service.AraaliAPIResponse>`__
      -  `MAraaliEndpoint <#araali_api_service.AraaliEndpoint>`__
      -  `MAraaliUser <#araali_api_service.AraaliUser>`__
      -  `MAsset <#araali_api_service.Asset>`__
      -  `MAssetFilter <#araali_api_service.AssetFilter>`__
      -  `MCapabilities <#araali_api_service.Capabilities>`__
      -  `MCreateTenantRequest <#araali_api_service.CreateTenantRequest>`__
      -  `MCreateTenantResponse <#araali_api_service.CreateTenantResponse>`__
      -  `MDeleteTenantRequest <#araali_api_service.DeleteTenantRequest>`__
      -  `MDeleteUserRequest <#araali_api_service.DeleteUserRequest>`__
      -  `MEndPoint <#araali_api_service.EndPoint>`__
      -  `MInsight <#araali_api_service.Insight>`__
      -  `MLens <#araali_api_service.Lens>`__
      -  `MLink <#araali_api_service.Link>`__
      -  `MListAlertsRequest <#araali_api_service.ListAlertsRequest>`__
      -  `MListAlertsResponse <#araali_api_service.ListAlertsResponse>`__
      -  `MListAssetsRequest <#araali_api_service.ListAssetsRequest>`__
      -  `MListAssetsResponse <#araali_api_service.ListAssetsResponse>`__
      -  `MListInsightsRequest <#araali_api_service.ListInsightsRequest>`__
      -  `MListInsightsResponse <#araali_api_service.ListInsightsResponse>`__
      -  `MListLinksRequest <#araali_api_service.ListLinksRequest>`__
      -  `MListLinksResponse <#araali_api_service.ListLinksResponse>`__
      -  `MNonAraaliClientEndpoint <#araali_api_service.NonAraaliClientEndpoint>`__
      -  `MNonAraaliEndpoint <#araali_api_service.NonAraaliEndpoint>`__
      -  `MNonAraaliServerEndpoint <#araali_api_service.NonAraaliServerEndpoint>`__
      -  `MPolicyInfo <#araali_api_service.PolicyInfo>`__
      -  `MPorts <#araali_api_service.Ports>`__
      -  `MSubnet <#araali_api_service.Subnet>`__
      -  `MTenant <#araali_api_service.Tenant>`__
      -  `MTimeSlice <#araali_api_service.TimeSlice>`__
      -  `MVulnerability <#araali_api_service.Vulnerability>`__
      -  `EAlertInfo.Status <#araali_api_service.AlertInfo.Status>`__
      -  `EAraaliAPIResponse.ReturnCode <#araali_api_service.AraaliAPIResponse.ReturnCode>`__
      -  `EAraaliUser.Role <#araali_api_service.AraaliUser.Role>`__
      -  `EAsset.AssetMode <#araali_api_service.Asset.AssetMode>`__
      -  `EAsset.AssetState <#araali_api_service.Asset.AssetState>`__
      -  `EAsset.AssetType <#araali_api_service.Asset.AssetType>`__
      -  `ELens.LensType <#araali_api_service.Lens.LensType>`__
      -  `ELink.LinkDirection <#araali_api_service.Link.LinkDirection>`__
      -  `ELinkState <#araali_api_service.LinkState>`__
      -  `ENonAraaliEndpoint.EndpointGroup <#araali_api_service.NonAraaliEndpoint.EndpointGroup>`__
      -  `EVulnerability.Severity <#araali_api_service.Vulnerability.Severity>`__
      -  `SAraaliAPI <#araali_api_service.AraaliAPI>`__

   -  `Scalar Value Types <#scalar-value-types>`__

.. container:: file-heading

   .. rubric:: araali_api_service.proto
      :name: araali_api_service.proto

   `Top <#title>`__

.. _araali_api_service.AddUserRequest:

AddUserRequest
~~~~~~~~~~~~~~

+--------+------------------------+-------+------------------------+
| Field  | Type                   | Label | Description            |
+========+========================+=======+========================+
| tenant | `Tenant <#araali_      |       | Tenant of the user     |
|        | api_service.Tenant>`__ |       | being added            |
+--------+------------------------+-------+------------------------+
| user   | `Ar                    |       | Information required   |
|        | aaliUser <#araali_api_ |       | to create the tenant   |
|        | service.AraaliUser>`__ |       |                        |
+--------+------------------------+-------+------------------------+

.. _araali_api_service.AlertFilter:

AlertFilter
~~~~~~~~~~~

Fields to filter alerts in the ListAlerts API.

+-------------------+-------------------+-------+-------------------+
| Field             | Type              | Label | Description       |
+===================+===================+=======+===================+
| open_alerts       | `bool <#bool>`__  |       | Fetch open alerts |
+-------------------+-------------------+-------+-------------------+
| closed_alerts     | `bool <#bool>`__  |       | Fetch closed      |
|                   |                   |       | alerts            |
+-------------------+-------------------+-------+-------------------+
| perimeter_egress  | `bool <#bool>`__  |       | Fetch perimeter   |
|                   |                   |       | egress alerts     |
+-------------------+-------------------+-------+-------------------+
| perimeter_ingress | `bool <#bool>`__  |       | Fetch perimeter   |
|                   |                   |       | ingress alerts    |
+-------------------+-------------------+-------+-------------------+
| home_             | `bool <#bool>`__  |       | Fetch non araali  |
| non_araali_egress |                   |       | egress alerts     |
|                   |                   |       | from private      |
|                   |                   |       | subnets           |
+-------------------+-------------------+-------+-------------------+
| home_n            | `bool <#bool>`__  |       | Fetch non araali  |
| on_araali_ingress |                   |       | ingress alerts    |
|                   |                   |       | from private      |
|                   |                   |       | subnets           |
+-------------------+-------------------+-------+-------------------+
| araali_to_araali  | `bool <#bool>`__  |       | Fetch araali to   |
|                   |                   |       | araali alerts     |
+-------------------+-------------------+-------+-------------------+
| list_all_alerts   | `bool <#bool>`__  |       | Fetch all alerts  |
|                   |                   |       | from all lenses,  |
|                   |                   |       | even ones not     |
|                   |                   |       | monitored by      |
|                   |                   |       | current user      |
+-------------------+-------------------+-------+-------------------+
| time              | `TimeSlice        |       | Time range in     |
|                   | <#araali_api_serv |       | which to fetch    |
|                   | ice.TimeSlice>`__ |       | alerts            |
+-------------------+-------------------+-------+-------------------+

.. _araali_api_service.AlertInfo:

AlertInfo
~~~~~~~~~

Additional information about alerts

+-------------------+-------------------+-------+-------------------+
| Field             | Type              | Label | Description       |
+===================+===================+=======+===================+
| communi           | `st               |       | Alert type        |
| cation_alert_type | ring <#string>`__ |       |                   |
+-------------------+-------------------+-------+-------------------+
| p                 | `st               |       | Process alert     |
| rocess_alert_type | ring <#string>`__ |       | type              |
+-------------------+-------------------+-------+-------------------+
| re_open_count     | `ui               |       | Number of times   |
|                   | nt32 <#uint32>`__ |       | transitioned from |
|                   |                   |       | SNOOZED -> ALERT  |
+-------------------+-------------------+-------+-------------------+
| status            | `AlertIn          |       | Whether OPEN or   |
|                   | fo.Status <#araal |       | CLOSED            |
|                   | i_api_service.Ale |       |                   |
|                   | rtInfo.Status>`__ |       |                   |
+-------------------+-------------------+-------+-------------------+

.. _araali_api_service.AraaliAPIResponse:

AraaliAPIResponse
~~~~~~~~~~~~~~~~~

Generic API response object.

+---------+------------------------+-------+------------------------+
| Field   | Type                   | Label | Description            |
+=========+========================+=======+========================+
| code    | `AraaliAPIRespons      |       | Success/Failure of API |
|         | e.ReturnCode <#araali_ |       | call                   |
|         | api_service.AraaliAPIR |       |                        |
|         | esponse.ReturnCode>`__ |       |                        |
+---------+------------------------+-------+------------------------+
| message | `string <#string>`__   |       | Custom message         |
|         |                        |       | returned by the        |
|         |                        |       | service if any         |
+---------+------------------------+-------+------------------------+

.. _araali_api_service.AraaliEndpoint:

AraaliEndpoint
~~~~~~~~~~~~~~

Represents an araali endpoint

+----------------+-------------------+-------+-------------------+
| Field          | Type              | Label | Description       |
+================+===================+=======+===================+
| zone           | `st               |       | Zone the endpoint |
|                | ring <#string>`__ |       | belongs to        |
+----------------+-------------------+-------+-------------------+
| app            | `st               |       | Mapped app the    |
|                | ring <#string>`__ |       | endpoint belongs  |
|                |                   |       | to                |
+----------------+-------------------+-------+-------------------+
| unmapped_app   | `st               |       | Original          |
|                | ring <#string>`__ |       | app/namespace the |
|                |                   |       | endpoint belongs  |
|                |                   |       | to                |
+----------------+-------------------+-------+-------------------+
| namespace      | `st               |       | Namespace of the  |
|                | ring <#string>`__ |       | endpoint          |
+----------------+-------------------+-------+-------------------+
| pod            | `st               |       | Pod the endpoint  |
|                | ring <#string>`__ |       | belongs to        |
+----------------+-------------------+-------+-------------------+
| container_name | `st               |       | Container the     |
|                | ring <#string>`__ |       | endpoint belongs  |
|                |                   |       | to                |
+----------------+-------------------+-------+-------------------+
| process        | `st               |       | Process of the    |
|                | ring <#string>`__ |       | endpoint belongs  |
|                |                   |       | to                |
+----------------+-------------------+-------+-------------------+
| binary_name    | `st               |       | Binary name of    |
|                | ring <#string>`__ |       | the endpoint      |
|                |                   |       | process           |
+----------------+-------------------+-------+-------------------+
| parent_process | `st               |       | Parent of the     |
|                | ring <#string>`__ |       | endpoint process  |
+----------------+-------------------+-------+-------------------+

.. _araali_api_service.AraaliUser:

AraaliUser
~~~~~~~~~~

User object identifying the user in API calls.

+---------------+---------------------+-------+---------------------+
| Field         | Type                | Label | Description         |
+===============+=====================+=======+=====================+
| email         | `                   |       | E-mail of the       |
|               | string <#string>`__ |       | registering user    |
+---------------+---------------------+-------+---------------------+
| role          | `AraaliUser.Role <# |       | Role of the         |
|               | araali_api_service. |       | registering user    |
|               | AraaliUser.Role>`__ |       |                     |
+---------------+---------------------+-------+---------------------+
| is_site_admin | `bool <#bool>`__    |       | Enables role to     |
|               |                     |       | have access to      |
|               |                     |       | zone-apps TRUE -    |
|               |                     |       | Enable modify       |
|               |                     |       | access to zone-apps |
|               |                     |       | FALSE - Enable      |
|               |                     |       | read-only access to |
|               |                     |       | zone-apps.          |
+---------------+---------------------+-------+---------------------+

.. _araali_api_service.Asset:

Asset
~~~~~

Representation of container/virtual machine information.

+------------------+------------------+----------+------------------+
| Field            | Type             | Label    | Description      |
+==================+==================+==========+==================+
| host_name        | `str             |          | Host name of     |
|                  | ing <#string>`__ |          | asset            |
+------------------+------------------+----------+------------------+
| ip_address       | `str             |          | IP address       |
|                  | ing <#string>`__ |          | assigned to the  |
|                  |                  |          | asset            |
+------------------+------------------+----------+------------------+
| uuid             | `str             |          | UUID if virtual  |
|                  | ing <#string>`__ |          | machine or       |
|                  |                  |          | container-id if  |
|                  |                  |          | container        |
+------------------+------------------+----------+------------------+
| image            | `str             |          | Container image  |
|                  | ing <#string>`__ |          | or ami-id for    |
|                  |                  |          | virtual machines |
+------------------+------------------+----------+------------------+
| zone             | `str             |          | Zone the asset   |
|                  | ing <#string>`__ |          | belongs to       |
+------------------+------------------+----------+------------------+
| apps             | `str             | repeated | Apps the asset   |
|                  | ing <#string>`__ |          | belongs to       |
+------------------+------------------+----------+------------------+
| state            | `Asset.Asse      |          | State of the     |
|                  | tState <#araali_ |          | asset active,    |
|                  | api_service.Asse |          | inactive etc     |
|                  | t.AssetState>`__ |          |                  |
+------------------+------------------+----------+------------------+
| asset_type       | `Asset.As        |          | Type of the      |
|                  | setType <#araali |          | asset            |
|                  | _api_service.Ass |          |                  |
|                  | et.AssetType>`__ |          |                  |
+------------------+------------------+----------+------------------+
| vulnerabilities  | `Vuln            | repeated | Vulnerabilities  |
|                  | erability <#araa |          | in the asset     |
|                  | li_api_service.V |          |                  |
|                  | ulnerability>`__ |          |                  |
+------------------+------------------+----------+------------------+
| mode             | `Asset.As        |          | Visibi           |
|                  | setMode <#araali |          | lity/Enforcement |
|                  | _api_service.Ass |          | mode of the      |
|                  | et.AssetMode>`__ |          | asset            |
+------------------+------------------+----------+------------------+
| os_name          | `str             |          | OS name of the   |
|                  | ing <#string>`__ |          | asset            |
+------------------+------------------+----------+------------------+
| iam_role         | `str             |          | AWS IAM Role     |
|                  | ing <#string>`__ |          | assigned to the  |
|                  |                  |          | asset            |
+------------------+------------------+----------+------------------+
| d                | `bool <#bool>`__ |          | Docker privilege |
| ocker_privileged |                  |          | assigned to the  |
|                  |                  |          | container        |
|                  |                  |          | (Docker          |
|                  |                  |          | containers only) |
+------------------+------------------+----------+------------------+
| docker           | `Ca              |          | Capabilities     |
|                  | pabilities <#ara |          | exported by      |
|                  | ali_api_service. |          | docker           |
|                  | Capabilities>`__ |          |                  |
+------------------+------------------+----------+------------------+
| containerd       | `Ca              |          | Capabilities     |
|                  | pabilities <#ara |          | exported by      |
|                  | ali_api_service. |          | containerd       |
|                  | Capabilities>`__ |          |                  |
+------------------+------------------+----------+------------------+

.. _araali_api_service.AssetFilter:

AssetFilter
~~~~~~~~~~~

Flags to filter assets in the ListAssets API.

+-------------------+------------------+-------+-------------------+
| Field             | Type             | Label | Description       |
+===================+==================+=======+===================+
| list_active_vm    | `bool <#bool>`__ |       | Return active     |
|                   |                  |       | virtual machines  |
+-------------------+------------------+-------+-------------------+
| list_inactive_vm  | `bool <#bool>`__ |       | Return inactive   |
|                   |                  |       | virtual machines  |
+-------------------+------------------+-------+-------------------+
| list              | `bool <#bool>`__ |       | Return active     |
| _active_container |                  |       | containers        |
+-------------------+------------------+-------+-------------------+
| list_i            | `bool <#bool>`__ |       | Return inactive   |
| nactive_container |                  |       | containers        |
+-------------------+------------------+-------+-------------------+

.. _araali_api_service.Capabilities:

Capabilities
~~~~~~~~~~~~

List of capabilities

============ ==================== ======== ===========
Field        Type                 Label    Description
============ ==================== ======== ===========
capabilities `string <#string>`__ repeated 
============ ==================== ======== ===========

.. _araali_api_service.CreateTenantRequest:

CreateTenantRequest
~~~~~~~~~~~~~~~~~~~

+--------+------------------------+-------+------------------------+
| Field  | Type                   | Label | Description            |
+========+========================+=======+========================+
| tenant | `Tenant <#araali_      |       | Information required   |
|        | api_service.Tenant>`__ |       | to create the tenant   |
+--------+------------------------+-------+------------------------+

.. _araali_api_service.CreateTenantResponse:

CreateTenantResponse
~~~~~~~~~~~~~~~~~~~~

+----------+-----------------------+-------+-----------------------+
| Field    | Type                  | Label | Description           |
+==========+=======================+=======+=======================+
| response | `AraaliAPIResponse    |       | Success/Failure of    |
|          | <#araali_api_service. |       | the API call          |
|          | AraaliAPIResponse>`__ |       |                       |
+----------+-----------------------+-------+-----------------------+
| tenant   | `Tenant <#araali_a    |       | Handle for the newly  |
|          | pi_service.Tenant>`__ |       | created tenant        |
+----------+-----------------------+-------+-----------------------+

.. _araali_api_service.DeleteTenantRequest:

DeleteTenantRequest
~~~~~~~~~~~~~~~~~~~

+--------+-----------------------------------------+-------+----------------------+
| Field  | Type                                    | Label | Description          |
+========+=========================================+=======+======================+
| tenant | `Tenant <#araali_api_service.Tenant>`__ |       | Tenant being deleted |
+--------+-----------------------------------------+-------+----------------------+

.. _araali_api_service.DeleteUserRequest:

DeleteUserRequest
~~~~~~~~~~~~~~~~~

+--------+------------------------+-------+------------------------+
| Field  | Type                   | Label | Description            |
+========+========================+=======+========================+
| tenant | `Tenant <#araali_      |       | Tenant of the user     |
|        | api_service.Tenant>`__ |       | being deleted          |
+--------+------------------------+-------+------------------------+
| user   | `Ar                    |       | Handle of the user     |
|        | aaliUser <#araali_api_ |       | being deleted          |
|        | service.AraaliUser>`__ |       |                        |
+--------+------------------------+-------+------------------------+

.. _araali_api_service.EndPoint:

EndPoint
~~~~~~~~

Represents one end of a link/alert_counts

+------------+----------------------+-------+----------------------+
| Field      | Type                 | Label | Description          |
+============+======================+=======+======================+
| araali     | `AraaliEndpoint      |       | Araali endpoint info |
|            |  <#araali_api_servic |       |                      |
|            | e.AraaliEndpoint>`__ |       |                      |
+------------+----------------------+-------+----------------------+
| non_araali | `                    |       | Non-Araali endpoint  |
|            | NonAraaliEndpoint <# |       | info                 |
|            | araali_api_service.N |       |                      |
|            | onAraaliEndpoint>`__ |       |                      |
+------------+----------------------+-------+----------------------+

.. _araali_api_service.Insight:

Insight
~~~~~~~

Instance of the insight Representation

+--------+-----------------------+----------+-----------------------+
| Field  | Type                  | Label    | Description           |
+========+=======================+==========+=======================+
| reason | `string <#string>`__  |          | The kind of insight   |
|        |                       |          | captured              |
+--------+-----------------------+----------+-----------------------+
| url    | `string <#string>`__  |          | The URL to view the   |
|        |                       |          | insights              |
+--------+-----------------------+----------+-----------------------+
| count  | `uint32 <#uint32>`__  |          | Number of insights    |
+--------+-----------------------+----------+-----------------------+
| lens   | `Lens <#araali        | repeated | The zone/app the      |
|        | _api_service.Lens>`__ |          | insights belong to    |
+--------+-----------------------+----------+-----------------------+

.. _araali_api_service.Lens:

Lens
~~~~

Drilled down entity/lens

+----------------+-------------------+-------+-------------------+
| Field          | Type              | Label | Description       |
+================+===================+=======+===================+
| type           | `L                |       | Lens type         |
|                | ens.LensType <#ar |       |                   |
|                | aali_api_service. |       |                   |
|                | Lens.LensType>`__ |       |                   |
+----------------+-------------------+-------+-------------------+
| zone           | `st               |       | Zone of the lens  |
|                | ring <#string>`__ |       |                   |
+----------------+-------------------+-------+-------------------+
| app            | `st               |       | App lens          |
|                | ring <#string>`__ |       |                   |
+----------------+-------------------+-------+-------------------+
| pod            | `st               |       | Pod of the lens   |
|                | ring <#string>`__ |       |                   |
+----------------+-------------------+-------+-------------------+
| container_name | `st               |       | Container of the  |
|                | ring <#string>`__ |       | lens              |
+----------------+-------------------+-------+-------------------+
| process        | `st               |       | Process of the    |
|                | ring <#string>`__ |       | lens              |
+----------------+-------------------+-------+-------------------+
| parent_process | `st               |       | Parent process of |
|                | ring <#string>`__ |       | the lens          |
+----------------+-------------------+-------+-------------------+
| binary_name    | `st               |       | Binary name of    |
|                | ring <#string>`__ |       | the lens          |
+----------------+-------------------+-------+-------------------+
| service        | `st               |       | Service lens      |
|                | ring <#string>`__ |       |                   |
+----------------+-------------------+-------+-------------------+

.. _araali_api_service.Link:

Link
~~~~

Represents an alert or policy link

+-------------+----------------------+-------+----------------------+
| Field       | Type                 | Label | Description          |
+=============+======================+=======+======================+
| client      | `En                  |       | Client endpoint      |
|             | dPoint <#araali_api_ |       |                      |
|             | service.EndPoint>`__ |       |                      |
+-------------+----------------------+-------+----------------------+
| server      | `En                  |       | Server endpoint      |
|             | dPoint <#araali_api_ |       |                      |
|             | service.EndPoint>`__ |       |                      |
+-------------+----------------------+-------+----------------------+
| direction   | `Li                  |       | Direction of         |
|             | nk.LinkDirection <#a |       | client-server link   |
|             | raali_api_service.Li |       |                      |
|             | nk.LinkDirection>`__ |       |                      |
+-------------+----------------------+-------+----------------------+
| timestamp   | `google.protobuf.T   |       | Timestamp when link  |
|             | imestamp <#google.pr |       | was discovered       |
|             | otobuf.Timestamp>`__ |       |                      |
+-------------+----------------------+-------+----------------------+
| unique_id   | `string <#string>`__ |       | Unique handle to the |
|             |                      |       | link                 |
+-------------+----------------------+-------+----------------------+
| state       | `Link                |       | State of the link    |
|             | State <#araali_api_s |       | alert,               |
|             | ervice.LinkState>`__ |       | active/snoozed etc   |
+-------------+----------------------+-------+----------------------+
| ports       | `Ports <#araali_a    |       | Aggregated           |
|             | pi_service.Ports>`__ |       | active/inactive      |
|             |                      |       | ports                |
+-------------+----------------------+-------+----------------------+
| alert_info  | `Aler                |       | Additional           |
|             | tInfo <#araali_api_s |       | information for      |
|             | ervice.AlertInfo>`__ |       | alerts               |
+-------------+----------------------+-------+----------------------+
| policy_info | `Policy              |       | Additional           |
|             | Info <#araali_api_se |       | information for      |
|             | rvice.PolicyInfo>`__ |       | policy links         |
+-------------+----------------------+-------+----------------------+

.. _araali_api_service.ListAlertsRequest:

ListAlertsRequest
~~~~~~~~~~~~~~~~~

Request for alerts received by tenant

+--------------+---------------------+-------+---------------------+
| Field        | Type                | Label | Description         |
+==============+=====================+=======+=====================+
| tenant       | `                   |       | Handle to tenant    |
|              | Tenant <#araali_api |       |                     |
|              | _service.Tenant>`__ |       |                     |
+--------------+---------------------+-------+---------------------+
| filter       | `AlertFilte         |       | Filter responses    |
|              | r <#araali_api_serv |       |                     |
|              | ice.AlertFilter>`__ |       |                     |
+--------------+---------------------+-------+---------------------+
| count        | `int32 <#int32>`__  |       | Number of alerts to |
|              |                     |       | be returned each    |
|              |                     |       | API call            |
+--------------+---------------------+-------+---------------------+
| paging_token | `                   |       | Token to be sent in |
|              | string <#string>`__ |       | the next API call   |
|              |                     |       | to retrieve the     |
|              |                     |       | next set of alerts  |
|              |                     |       | (paging)            |
+--------------+---------------------+-------+---------------------+

.. _araali_api_service.ListAlertsResponse:

ListAlertsResponse
~~~~~~~~~~~~~~~~~~

+--------------+--------------------+----------+--------------------+
| Field        | Type               | Label    | Description        |
+==============+====================+==========+====================+
| response     | `Araali            |          | ListAsset API call |
|              | APIResponse <#araa |          | response           |
|              | li_api_service.Ara |          |                    |
|              | aliAPIResponse>`__ |          |                    |
+--------------+--------------------+----------+--------------------+
| links        | `Link <#araali_ap  | repeated | List of alerts     |
|              | i_service.Link>`__ |          |                    |
+--------------+--------------------+----------+--------------------+
| paging_token | `s                 |          | Token to be passed |
|              | tring <#string>`__ |          | to the next API    |
|              |                    |          | call (indicating   |
|              |                    |          | there are more     |
|              |                    |          | alerts to be       |
|              |                    |          | retrieved)         |
+--------------+--------------------+----------+--------------------+

.. _araali_api_service.ListAssetsRequest:

ListAssetsRequest
~~~~~~~~~~~~~~~~~

Request for the list of assets (virtual machines/containers) in a
tenant.

+--------+------------------------+-------+------------------------+
| Field  | Type                   | Label | Description            |
+========+========================+=======+========================+
| tenant | `Tenant <#araali_      |       | Handle of the tenant   |
|        | api_service.Tenant>`__ |       |                        |
+--------+------------------------+-------+------------------------+
| zone   | `string <#string>`__   |       | Zone from which to     |
|        |                        |       | return assets          |
+--------+------------------------+-------+------------------------+
| app    | `string <#string>`__   |       | App/Namespace from     |
|        |                        |       | which to return assets |
+--------+------------------------+-------+------------------------+
| time   | `                      |       | Start/End time range   |
|        | TimeSlice <#araali_api |       | from which to return   |
|        | _service.TimeSlice>`__ |       | assets                 |
+--------+------------------------+-------+------------------------+
| filter | `Asse                  |       | Filter assets based on |
|        | tFilter <#araali_api_s |       | type and               |
|        | ervice.AssetFilter>`__ |       | active/inactive        |
+--------+------------------------+-------+------------------------+

.. _araali_api_service.ListAssetsResponse:

ListAssetsResponse
~~~~~~~~~~~~~~~~~~

+----------+----------------------+----------+----------------------+
| Field    | Type                 | Label    | Description          |
+==========+======================+==========+======================+
| response | `                    |          | ListAsset API call   |
|          | AraaliAPIResponse <# |          | response             |
|          | araali_api_service.A |          |                      |
|          | raaliAPIResponse>`__ |          |                      |
+----------+----------------------+----------+----------------------+
| assets   | `Asset <#araali_a    | repeated | List of assets       |
|          | pi_service.Asset>`__ |          |                      |
+----------+----------------------+----------+----------------------+

.. _araali_api_service.ListInsightsRequest:

ListInsightsRequest
~~~~~~~~~~~~~~~~~~~

+--------+------------------------+-------+------------------------+
| Field  | Type                   | Label | Description            |
+========+========================+=======+========================+
| tenant | `Tenant <#araali_      |       | Handle of tenant       |
|        | api_service.Tenant>`__ |       |                        |
+--------+------------------------+-------+------------------------+
| zone   | `string <#string>`__   |       | Zone where insights    |
|        |                        |       | are requested          |
+--------+------------------------+-------+------------------------+

.. _araali_api_service.ListInsightsResponse:

ListInsightsResponse
~~~~~~~~~~~~~~~~~~~~

+----------+----------------------+----------+----------------------+
| Field    | Type                 | Label    | Description          |
+==========+======================+==========+======================+
| response | `                    |          | ListInsights API     |
|          | AraaliAPIResponse <# |          | call response        |
|          | araali_api_service.A |          |                      |
|          | raaliAPIResponse>`__ |          |                      |
+----------+----------------------+----------+----------------------+
| insights | `                    | repeated | List of insights     |
|          | Insight <#araali_api |          |                      |
|          | _service.Insight>`__ |          |                      |
+----------+----------------------+----------+----------------------+

.. _araali_api_service.ListLinksRequest:

ListLinksRequest
~~~~~~~~~~~~~~~~

+---------+------------------------+-------+------------------------+
| Field   | Type                   | Label | Description            |
+=========+========================+=======+========================+
| tenant  | `Tenant <#araali_      |       | Handle for the tenant  |
|         | api_service.Tenant>`__ |       |                        |
+---------+------------------------+-------+------------------------+
| zone    | `string <#string>`__   |       | Zone for the request   |
+---------+------------------------+-------+------------------------+
| app     | `string <#string>`__   |       | App for the request    |
+---------+------------------------+-------+------------------------+
| service | `string <#string>`__   |       | Required when zone and |
|         |                        |       | app are not specified. |
|         |                        |       | Must be in form of     |
|         |                        |       | ip:port or fqdn:port   |
+---------+------------------------+-------+------------------------+
| time    | `                      |       | Time range for the     |
|         | TimeSlice <#araali_api |       | list links request     |
|         | _service.TimeSlice>`__ |       |                        |
+---------+------------------------+-------+------------------------+

.. _araali_api_service.ListLinksResponse:

ListLinksResponse
~~~~~~~~~~~~~~~~~

+----------+----------------------+----------+----------------------+
| Field    | Type                 | Label    | Description          |
+==========+======================+==========+======================+
| response | `                    |          | ListLinks API call   |
|          | AraaliAPIResponse <# |          | response             |
|          | araali_api_service.A |          |                      |
|          | raaliAPIResponse>`__ |          |                      |
+----------+----------------------+----------+----------------------+
| links    | `Link <#araali_      | repeated | List of links        |
|          | api_service.Link>`__ |          |                      |
+----------+----------------------+----------+----------------------+

.. _araali_api_service.NonAraaliClientEndpoint:

NonAraaliClientEndpoint
~~~~~~~~~~~~~~~~~~~~~~~

Represents a non araali client endpoint

====== ======================================= ===== =============
Field  Type                                    Label Description
====== ======================================= ===== =============
subnet `Subnet <#araali_api_service.Subnet>`__       Client subnet
====== ======================================= ===== =============

.. _araali_api_service.NonAraaliEndpoint:

NonAraaliEndpoint
~~~~~~~~~~~~~~~~~

Represents a non araali endpoint

+----------------+-------------------+-------+-------------------+
| Field          | Type              | Label | Description       |
+================+===================+=======+===================+
| client         | `NonA             |       | Non araali client |
|                | raaliClientEndpoi |       |                   |
|                | nt <#araali_api_s |       |                   |
|                | ervice.NonAraaliC |       |                   |
|                | lientEndpoint>`__ |       |                   |
+----------------+-------------------+-------+-------------------+
| server         | `NonA             |       | Non araali server |
|                | raaliServerEndpoi |       |                   |
|                | nt <#araali_api_s |       |                   |
|                | ervice.NonAraaliS |       |                   |
|                | erverEndpoint>`__ |       |                   |
+----------------+-------------------+-------+-------------------+
| endpoint_group | `Non              |       | WORLD if public   |
|                | AraaliEndpoint.En |       | subnet. HOME if   |
|                | dpointGroup <#ara |       | private subnet.   |
|                | ali_api_service.N |       |                   |
|                | onAraaliEndpoint. |       |                   |
|                | EndpointGroup>`__ |       |                   |
+----------------+-------------------+-------+-------------------+
| organization   | `st               |       | Autonomous System |
|                | ring <#string>`__ |       | Organization of   |
|                |                   |       | the IP address if |
|                |                   |       | available         |
+----------------+-------------------+-------+-------------------+

.. _araali_api_service.NonAraaliServerEndpoint:

NonAraaliServerEndpoint
~~~~~~~~~~~~~~~~~~~~~~~

Represents a non araali server endpoint

+-------------+----------------------+-------+----------------------+
| Field       | Type                 | Label | Description          |
+=============+======================+=======+======================+
| dns_pattern | `string <#string>`__ |       | DNS/FQDN of endpoint |
+-------------+----------------------+-------+----------------------+
| subnet      | `Subnet <#araali_ap  |       | Server subnet        |
|             | i_service.Subnet>`__ |       |                      |
+-------------+----------------------+-------+----------------------+
| dst_port    | `uint32 <#uint32>`__ |       | Service destination  |
|             |                      |       | port                 |
+-------------+----------------------+-------+----------------------+

.. _araali_api_service.PolicyInfo:

PolicyInfo
~~~~~~~~~~

Additional information about policy

+-------------------+-------------------+-------+-------------------+
| Field             | Type              | Label | Description       |
+===================+===================+=======+===================+
| template_name     | `st               |       | Template name     |
|                   | ring <#string>`__ |       | used to validate  |
|                   |                   |       | the link          |
+-------------------+-------------------+-------+-------------------+
| template_user     | `st               |       | User who created  |
|                   | ring <#string>`__ |       | the template to   |
|                   |                   |       | validate the link |
+-------------------+-------------------+-------+-------------------+
| p                 | `st               |       | Reason for        |
| olicy_skip_reason | ring <#string>`__ |       | skipping policy   |
|                   |                   |       | evaluation at     |
|                   |                   |       | agents when       |
|                   |                   |       | enforced          |
+-------------------+-------------------+-------+-------------------+

.. _araali_api_service.Ports:

Ports
~~~~~

+----------------+------------------+----------+------------------+
| Field          | Type             | Label    | Description      |
+================+==================+==========+==================+
| active_ports   | `uin             | repeated | Active           |
|                | t32 <#uint32>`__ |          | aggregated ports |
|                |                  |          | in the link      |
+----------------+------------------+----------+------------------+
| inactive_ports | `uin             | repeated | Inactive         |
|                | t32 <#uint32>`__ |          | aggregated ports |
|                |                  |          | in the link      |
+----------------+------------------+----------+------------------+

.. _araali_api_service.Subnet:

Subnet
~~~~~~

Represents the subnet/mask

======== ==================== ===== ==============
Field    Type                 Label Description
======== ==================== ===== ==============
subnet   `string <#string>`__       Client subnet
net_mask `uint32 <#uint32>`__       Client netmask
======== ==================== ===== ==============

.. _araali_api_service.Tenant:

Tenant
~~~~~~

Tenant object identifying the tenant in API calls.

+-------------+----------------------+-------+----------------------+
| Field       | Type                 | Label | Description          |
+=============+======================+=======+======================+
| id          | `string <#string>`__ |       | Id of the tenant     |
+-------------+----------------------+-------+----------------------+
| admin_email | `string <#string>`__ |       | Admin e-mail of the  |
|             |                      |       | tenant. Also adds an |
|             |                      |       | ADMIN role user in   |
|             |                      |       | this tenant.         |
+-------------+----------------------+-------+----------------------+

.. _araali_api_service.TimeSlice:

TimeSlice
~~~~~~~~~

Object for specifying start and end time in varous API calls.

+------------+----------------------+-------+----------------------+
| Field      | Type                 | Label | Description          |
+============+======================+=======+======================+
| start_time | `google.protobuf.T   |       | Start time to fetch  |
|            | imestamp <#google.pr |       | from. Specify 0 to   |
|            | otobuf.Timestamp>`__ |       | indicate beginning   |
|            |                      |       | of time              |
+------------+----------------------+-------+----------------------+
| end_time   | `google.protobuf.T   |       | End time to fetch up |
|            | imestamp <#google.pr |       | to                   |
|            | otobuf.Timestamp>`__ |       |                      |
+------------+----------------------+-------+----------------------+

.. _araali_api_service.Vulnerability:

Vulnerability
~~~~~~~~~~~~~

Captures an instance of vulnerability package name, cve info etc

+--------------+--------------------+----------+--------------------+
| Field        | Type               | Label    | Description        |
+==============+====================+==========+====================+
| package_name | `s                 |          | Package name with  |
|              | tring <#string>`__ |          | the vulnerability  |
+--------------+--------------------+----------+--------------------+
| cve_id       | `s                 | repeated | CVE id of the      |
|              | tring <#string>`__ |          | vulnerability      |
+--------------+--------------------+----------+--------------------+
| severity     | `Vulnerability.Se  |          | Severity of the    |
|              | verity <#araali_ap |          | vulnerability      |
|              | i_service.Vulnerab |          |                    |
|              | ility.Severity>`__ |          |                    |
+--------------+--------------------+----------+--------------------+

.. _araali_api_service.AlertInfo.Status:

AlertInfo.Status
~~~~~~~~~~~~~~~~

============== ====== ===========
Name           Number Description
============== ====== ===========
UNKNOWN_STATUS 0      
OPEN           1      
CLOSED         2      
============== ====== ===========

.. _araali_api_service.AraaliAPIResponse.ReturnCode:

AraaliAPIResponse.ReturnCode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Return status codes for the Araali APIs

======= ====== ====================================
Name    Number Description
======= ====== ====================================
SUCCESS 0      API call succeeded
FAILURE 1      API call failed
UNKNOWN 2      Status unknown (Should never happen)
======= ====== ====================================

.. _araali_api_service.AraaliUser.Role:

AraaliUser.Role
~~~~~~~~~~~~~~~

Enum for specifying the role of a user

===== ====== ==========================================
Name  Number Description
===== ====== ==========================================
ADMIN 0      Enables user to create, modify other users
USER  1      Set if the user is not an administrator
===== ====== ==========================================

.. _araali_api_service.Asset.AssetMode:

Asset.AssetMode
~~~~~~~~~~~~~~~

Mode the asset is in

TAP - Tap's into telemetry to discover policies (no enforcement).

INLINE - Firewall embedded inline to enforce policies if needed
(enforcement).

=========================== ====== ================================
Name                        Number Description
=========================== ====== ================================
TAP                         0      No enforcement/visibility mode
INLINE                      1      Inline enforcement mode
TRANSITIONING_TAP_TO_INLINE 2      Transitioning from TAP to INLINE
TRANSITIONING_INLINE_TO_TAP 3      Transitioning from INLINE to TAP
=========================== ====== ================================

.. _araali_api_service.Asset.AssetState:

Asset.AssetState
~~~~~~~~~~~~~~~~

State of the asset

======== ====== ======================
Name     Number Description
======== ====== ======================
DELETED  0      Asset has been deleted
ACTIVE   1      Asset is active
INACTIVE 2      Asset is inactive
======== ====== ======================

.. _araali_api_service.Asset.AssetType:

Asset.AssetType
~~~~~~~~~~~~~~~

Type of the asset

=============== ====== ====================
Name            Number Description
=============== ====== ====================
UNKNOWN_ASSET   0      Unknown asset type
VIRTUAL_MACHINE 1      Virtual Machine type
CONTAINER       2      Container type
=============== ====== ====================

.. _araali_api_service.Lens.LensType:

Lens.LensType
~~~~~~~~~~~~~

Type of lens

============ ====== ===============
Name         Number Description
============ ====== ===============
UNKNOWN_LENS 0      Unspecified
ZONE_APP     1      Zone/App level
SERVICE      2      Service level
ZONE         3      Zone level
PROCESS      4      Process level
CONTAINER    5      Container level
TENANT       6      Tenant level
============ ====== ===============

.. _araali_api_service.Link.LinkDirection:

Link.LinkDirection
~~~~~~~~~~~~~~~~~~

Direction of the link araali-araali, araali-ingress etc

+--------------------+--------+-------------------------------------------------+
| Name               | Number | Description                                     |
+====================+========+=================================================+
| UNKNOWN_DIRECTION  | 0      | Unknown                                         |
+--------------------+--------+-------------------------------------------------+
| NON_ARAALI_INGRESS | 1      | Ingress from an unprotected non-araali endpoint |
+--------------------+--------+-------------------------------------------------+
| ARAALI_INGRESS     | 2      | Ingress from an araali protected endpoint       |
+--------------------+--------+-------------------------------------------------+
| NON_ARAALI_EGRESS  | 3      | Egress to an unprotected non-araali endpoint    |
+--------------------+--------+-------------------------------------------------+
| ARAALI_EGRESS      | 4      | Egress to an araali protected endpoint          |
+--------------------+--------+-------------------------------------------------+
| INTERNAL           | 5      | Link between two araali endpoints within an app |
+--------------------+--------+-------------------------------------------------+

.. _araali_api_service.LinkState:

LinkState
~~~~~~~~~

Type of a link Alert or PolicyInfo

============== ====== ==============================================
Name           Number Description
============== ====== ==============================================
BASELINE_ALERT 0      Alert
DEFINED_POLICY 1      Currently active policy
SNOOZED_POLICY 2      Policy that was discovered but removed/snoozed
DENIED_POLICY  3      Deny policy
============== ====== ==============================================

.. _araali_api_service.NonAraaliEndpoint.EndpointGroup:

NonAraaliEndpoint.EndpointGroup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

============= ====== ===========
Name          Number Description
============= ====== ===========
UNKNOWN_GROUP 0      
WORLD         1      
HOME          2      
============= ====== ===========

.. _araali_api_service.Vulnerability.Severity:

Vulnerability.Severity
~~~~~~~~~~~~~~~~~~~~~~

======== ====== =================
Name     Number Description
======== ====== =================
NONE     0      No severity
LOW      1      Low severity
MEDIUM   2      Medium severity
HIGH     3      High severity
CRITICAL 4      Critical severity
======== ====== =================

.. _araali_api_service.AraaliAPI:

AraaliAPI
~~~~~~~~~

+--------------+----------------+----------------+----------------+
| Method Name  | Request Type   | Response Type  | Description    |
+==============+================+================+================+
| createTenant | `CreateTe      | `CreateTena    | Add a tenant   |
|              | nantRequest <# | ntResponse <#a |                |
|              | araali_api_ser | raali_api_serv |                |
|              | vice.CreateTen | ice.CreateTena |                |
|              | antRequest>`__ | ntResponse>`__ |                |
+--------------+----------------+----------------+----------------+
| deleteTenant | `DeleteTe      | `Araa          | Delete a       |
|              | nantRequest <# | liAPIResponse  | tenant         |
|              | araali_api_ser | <#araali_api_s |                |
|              | vice.DeleteTen | ervice.AraaliA |                |
|              | antRequest>`__ | PIResponse>`__ |                |
+--------------+----------------+----------------+----------------+
| addUser      | `AddUserReque  | `Araa          | Add a user     |
|              | st <#araali_ap | liAPIResponse  |                |
|              | i_service.AddU | <#araali_api_s |                |
|              | serRequest>`__ | ervice.AraaliA |                |
|              |                | PIResponse>`__ |                |
+--------------+----------------+----------------+----------------+
| deleteUser   | `Dele          | `Araa          | Delete a user  |
|              | teUserRequest  | liAPIResponse  |                |
|              | <#araali_api_s | <#araali_api_s |                |
|              | ervice.DeleteU | ervice.AraaliA |                |
|              | serRequest>`__ | PIResponse>`__ |                |
+--------------+----------------+----------------+----------------+
| listAssets   | `List          | `ListAs        | Get assets     |
|              | AssetsRequest  | setsResponse < |                |
|              | <#araali_api_s | #araali_api_se |                |
|              | ervice.ListAss | rvice.ListAsse |                |
|              | etsRequest>`__ | tsResponse>`__ |                |
+--------------+----------------+----------------+----------------+
| listAlerts   | `List          | `ListAl        | Get alerts     |
|              | AlertsRequest  | ertsResponse < |                |
|              | <#araali_api_s | #araali_api_se |                |
|              | ervice.ListAle | rvice.ListAler |                |
|              | rtsRequest>`__ | tsResponse>`__ |                |
+--------------+----------------+----------------+----------------+
| listLinks    | `Li            | `List          | Get links      |
|              | stLinksRequest | LinksResponse  | within a       |
|              |  <#araali_api_ | <#araali_api_s | zone/app       |
|              | service.ListLi | ervice.ListLin |                |
|              | nksRequest>`__ | ksResponse>`__ |                |
+--------------+----------------+----------------+----------------+
| listInsights | `ListInsi      | `ListInsigh    | Get tenant     |
|              | ghtsRequest <# | tsResponse <#a | wide insights  |
|              | araali_api_ser | raali_api_serv |                |
|              | vice.ListInsig | ice.ListInsigh |                |
|              | htsRequest>`__ | tsResponse>`__ |                |
+--------------+----------------+----------------+----------------+

Scalar Value Types
------------------

+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| .     | Notes | C++   | Java  | P     | Go    | C#    | PHP   | Ruby  |
| proto |       |       |       | ython |       |       |       |       |
| Type  |       |       |       |       |       |       |       |       |
+=======+=======+=======+=======+=======+=======+=======+=======+=======+
| d     |       | d     | d     | float | fl    | d     | float | Float |
| ouble |       | ouble | ouble |       | oat64 | ouble |       |       |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| float |       | float | float | float | fl    | float | float | Float |
|       |       |       |       |       | oat32 |       |       |       |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| int32 | Uses  | int32 | int   | int   | int32 | int   | in    | B     |
|       | varia |       |       |       |       |       | teger | ignum |
|       | ble-l |       |       |       |       |       |       | or    |
|       | ength |       |       |       |       |       |       | F     |
|       | enco  |       |       |       |       |       |       | ixnum |
|       | ding. |       |       |       |       |       |       | (as   |
|       | I     |       |       |       |       |       |       | requ  |
|       | neffi |       |       |       |       |       |       | ired) |
|       | cient |       |       |       |       |       |       |       |
|       | for   |       |       |       |       |       |       |       |
|       | enc   |       |       |       |       |       |       |       |
|       | oding |       |       |       |       |       |       |       |
|       | neg   |       |       |       |       |       |       |       |
|       | ative |       |       |       |       |       |       |       |
|       | nu    |       |       |       |       |       |       |       |
|       | mbers |       |       |       |       |       |       |       |
|       | – if  |       |       |       |       |       |       |       |
|       | your  |       |       |       |       |       |       |       |
|       | field |       |       |       |       |       |       |       |
|       | is    |       |       |       |       |       |       |       |
|       | l     |       |       |       |       |       |       |       |
|       | ikely |       |       |       |       |       |       |       |
|       | to    |       |       |       |       |       |       |       |
|       | have  |       |       |       |       |       |       |       |
|       | neg   |       |       |       |       |       |       |       |
|       | ative |       |       |       |       |       |       |       |
|       | va    |       |       |       |       |       |       |       |
|       | lues, |       |       |       |       |       |       |       |
|       | use   |       |       |       |       |       |       |       |
|       | s     |       |       |       |       |       |       |       |
|       | int32 |       |       |       |       |       |       |       |
|       | ins   |       |       |       |       |       |       |       |
|       | tead. |       |       |       |       |       |       |       |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| int64 | Uses  | int64 | long  | int   | int64 | long  | inte  | B     |
|       | varia |       |       | /long |       |       | ger/s | ignum |
|       | ble-l |       |       |       |       |       | tring |       |
|       | ength |       |       |       |       |       |       |       |
|       | enco  |       |       |       |       |       |       |       |
|       | ding. |       |       |       |       |       |       |       |
|       | I     |       |       |       |       |       |       |       |
|       | neffi |       |       |       |       |       |       |       |
|       | cient |       |       |       |       |       |       |       |
|       | for   |       |       |       |       |       |       |       |
|       | enc   |       |       |       |       |       |       |       |
|       | oding |       |       |       |       |       |       |       |
|       | neg   |       |       |       |       |       |       |       |
|       | ative |       |       |       |       |       |       |       |
|       | nu    |       |       |       |       |       |       |       |
|       | mbers |       |       |       |       |       |       |       |
|       | – if  |       |       |       |       |       |       |       |
|       | your  |       |       |       |       |       |       |       |
|       | field |       |       |       |       |       |       |       |
|       | is    |       |       |       |       |       |       |       |
|       | l     |       |       |       |       |       |       |       |
|       | ikely |       |       |       |       |       |       |       |
|       | to    |       |       |       |       |       |       |       |
|       | have  |       |       |       |       |       |       |       |
|       | neg   |       |       |       |       |       |       |       |
|       | ative |       |       |       |       |       |       |       |
|       | va    |       |       |       |       |       |       |       |
|       | lues, |       |       |       |       |       |       |       |
|       | use   |       |       |       |       |       |       |       |
|       | s     |       |       |       |       |       |       |       |
|       | int64 |       |       |       |       |       |       |       |
|       | ins   |       |       |       |       |       |       |       |
|       | tead. |       |       |       |       |       |       |       |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| u     | Uses  | u     | int   | int   | u     | uint  | in    | B     |
| int32 | varia | int32 |       | /long | int32 |       | teger | ignum |
|       | ble-l |       |       |       |       |       |       | or    |
|       | ength |       |       |       |       |       |       | F     |
|       | enco  |       |       |       |       |       |       | ixnum |
|       | ding. |       |       |       |       |       |       | (as   |
|       |       |       |       |       |       |       |       | requ  |
|       |       |       |       |       |       |       |       | ired) |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| u     | Uses  | u     | long  | int   | u     | ulong | inte  | B     |
| int64 | varia | int64 |       | /long | int64 |       | ger/s | ignum |
|       | ble-l |       |       |       |       |       | tring | or    |
|       | ength |       |       |       |       |       |       | F     |
|       | enco  |       |       |       |       |       |       | ixnum |
|       | ding. |       |       |       |       |       |       | (as   |
|       |       |       |       |       |       |       |       | requ  |
|       |       |       |       |       |       |       |       | ired) |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| s     | Uses  | int32 | int   | int   | int32 | int   | in    | B     |
| int32 | varia |       |       |       |       |       | teger | ignum |
|       | ble-l |       |       |       |       |       |       | or    |
|       | ength |       |       |       |       |       |       | F     |
|       | enco  |       |       |       |       |       |       | ixnum |
|       | ding. |       |       |       |       |       |       | (as   |
|       | S     |       |       |       |       |       |       | requ  |
|       | igned |       |       |       |       |       |       | ired) |
|       | int   |       |       |       |       |       |       |       |
|       | v     |       |       |       |       |       |       |       |
|       | alue. |       |       |       |       |       |       |       |
|       | These |       |       |       |       |       |       |       |
|       | more  |       |       |       |       |       |       |       |
|       | e     |       |       |       |       |       |       |       |
|       | ffici |       |       |       |       |       |       |       |
|       | ently |       |       |       |       |       |       |       |
|       | e     |       |       |       |       |       |       |       |
|       | ncode |       |       |       |       |       |       |       |
|       | neg   |       |       |       |       |       |       |       |
|       | ative |       |       |       |       |       |       |       |
|       | nu    |       |       |       |       |       |       |       |
|       | mbers |       |       |       |       |       |       |       |
|       | than  |       |       |       |       |       |       |       |
|       | re    |       |       |       |       |       |       |       |
|       | gular |       |       |       |       |       |       |       |
|       | in    |       |       |       |       |       |       |       |
|       | t32s. |       |       |       |       |       |       |       |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| s     | Uses  | int64 | long  | int   | int64 | long  | inte  | B     |
| int64 | varia |       |       | /long |       |       | ger/s | ignum |
|       | ble-l |       |       |       |       |       | tring |       |
|       | ength |       |       |       |       |       |       |       |
|       | enco  |       |       |       |       |       |       |       |
|       | ding. |       |       |       |       |       |       |       |
|       | S     |       |       |       |       |       |       |       |
|       | igned |       |       |       |       |       |       |       |
|       | int   |       |       |       |       |       |       |       |
|       | v     |       |       |       |       |       |       |       |
|       | alue. |       |       |       |       |       |       |       |
|       | These |       |       |       |       |       |       |       |
|       | more  |       |       |       |       |       |       |       |
|       | e     |       |       |       |       |       |       |       |
|       | ffici |       |       |       |       |       |       |       |
|       | ently |       |       |       |       |       |       |       |
|       | e     |       |       |       |       |       |       |       |
|       | ncode |       |       |       |       |       |       |       |
|       | neg   |       |       |       |       |       |       |       |
|       | ative |       |       |       |       |       |       |       |
|       | nu    |       |       |       |       |       |       |       |
|       | mbers |       |       |       |       |       |       |       |
|       | than  |       |       |       |       |       |       |       |
|       | re    |       |       |       |       |       |       |       |
|       | gular |       |       |       |       |       |       |       |
|       | in    |       |       |       |       |       |       |       |
|       | t64s. |       |       |       |       |       |       |       |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| fi    | A     | u     | int   | int   | u     | uint  | in    | B     |
| xed32 | lways | int32 |       |       | int32 |       | teger | ignum |
|       | four  |       |       |       |       |       |       | or    |
|       | b     |       |       |       |       |       |       | F     |
|       | ytes. |       |       |       |       |       |       | ixnum |
|       | More  |       |       |       |       |       |       | (as   |
|       | effi  |       |       |       |       |       |       | requ  |
|       | cient |       |       |       |       |       |       | ired) |
|       | than  |       |       |       |       |       |       |       |
|       | u     |       |       |       |       |       |       |       |
|       | int32 |       |       |       |       |       |       |       |
|       | if    |       |       |       |       |       |       |       |
|       | v     |       |       |       |       |       |       |       |
|       | alues |       |       |       |       |       |       |       |
|       | are   |       |       |       |       |       |       |       |
|       | often |       |       |       |       |       |       |       |
|       | gr    |       |       |       |       |       |       |       |
|       | eater |       |       |       |       |       |       |       |
|       | than  |       |       |       |       |       |       |       |
|       | 2^28. |       |       |       |       |       |       |       |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| fi    | A     | u     | long  | int   | u     | ulong | inte  | B     |
| xed64 | lways | int64 |       | /long | int64 |       | ger/s | ignum |
|       | eight |       |       |       |       |       | tring |       |
|       | b     |       |       |       |       |       |       |       |
|       | ytes. |       |       |       |       |       |       |       |
|       | More  |       |       |       |       |       |       |       |
|       | effi  |       |       |       |       |       |       |       |
|       | cient |       |       |       |       |       |       |       |
|       | than  |       |       |       |       |       |       |       |
|       | u     |       |       |       |       |       |       |       |
|       | int64 |       |       |       |       |       |       |       |
|       | if    |       |       |       |       |       |       |       |
|       | v     |       |       |       |       |       |       |       |
|       | alues |       |       |       |       |       |       |       |
|       | are   |       |       |       |       |       |       |       |
|       | often |       |       |       |       |       |       |       |
|       | gr    |       |       |       |       |       |       |       |
|       | eater |       |       |       |       |       |       |       |
|       | than  |       |       |       |       |       |       |       |
|       | 2^56. |       |       |       |       |       |       |       |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| sfi   | A     | int32 | int   | int   | int32 | int   | in    | B     |
| xed32 | lways |       |       |       |       |       | teger | ignum |
|       | four  |       |       |       |       |       |       | or    |
|       | b     |       |       |       |       |       |       | F     |
|       | ytes. |       |       |       |       |       |       | ixnum |
|       |       |       |       |       |       |       |       | (as   |
|       |       |       |       |       |       |       |       | requ  |
|       |       |       |       |       |       |       |       | ired) |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| sfi   | A     | int64 | long  | int   | int64 | long  | inte  | B     |
| xed64 | lways |       |       | /long |       |       | ger/s | ignum |
|       | eight |       |       |       |       |       | tring |       |
|       | b     |       |       |       |       |       |       |       |
|       | ytes. |       |       |       |       |       |       |       |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| bool  |       | bool  | bo    | bo    | bool  | bool  | bo    | TrueC |
|       |       |       | olean | olean |       |       | olean | lass/ |
|       |       |       |       |       |       |       |       | False |
|       |       |       |       |       |       |       |       | Class |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| s     | A     | s     | S     | s     | s     | s     | s     | S     |
| tring | s     | tring | tring | tr/un | tring | tring | tring | tring |
|       | tring |       |       | icode |       |       |       | (U    |
|       | must  |       |       |       |       |       |       | TF-8) |
|       | a     |       |       |       |       |       |       |       |
|       | lways |       |       |       |       |       |       |       |
|       | co    |       |       |       |       |       |       |       |
|       | ntain |       |       |       |       |       |       |       |
|       | UTF-8 |       |       |       |       |       |       |       |
|       | en    |       |       |       |       |       |       |       |
|       | coded |       |       |       |       |       |       |       |
|       | or    |       |       |       |       |       |       |       |
|       | 7-bit |       |       |       |       |       |       |       |
|       | ASCII |       |       |       |       |       |       |       |
|       | text. |       |       |       |       |       |       |       |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| bytes | May   | s     | ByteS | str   | [     | ByteS | s     | S     |
|       | co    | tring | tring |       | ]byte | tring | tring | tring |
|       | ntain |       |       |       |       |       |       | (A    |
|       | any   |       |       |       |       |       |       | SCII- |
|       | arbi  |       |       |       |       |       |       | 8BIT) |
|       | trary |       |       |       |       |       |       |       |
|       | seq   |       |       |       |       |       |       |       |
|       | uence |       |       |       |       |       |       |       |
|       | of    |       |       |       |       |       |       |       |
|       | b     |       |       |       |       |       |       |       |
|       | ytes. |       |       |       |       |       |       |       |
+-------+-------+-------+-------+-------+-------+-------+-------+-------+
