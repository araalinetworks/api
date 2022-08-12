Golang SDK API
--------------

Functions
=========
Must import ``api/api`` for all functions to work

TenantCreate()
**************

Create a tenant

.. tabs::
  .. code-tab:: go

        api.TenantCreate(name, adminName, adminEmail string, freemium bool)


TenantDelete()
**************

Delete a tenant

.. tabs::
  .. code-tab:: go

        api.TenantDelete(tenant string)


UserAdd()
**************

Add a User

.. tabs::
  .. code-tab:: go

        api.UserAdd(tenant, userName, userEmail, role string)


UserDelete()
**************

Delete a User

.. tabs::
  .. code-tab:: go

        api.UserDelete(tenant, userEmail string)


ListAssets()
**************

Get assets

.. tabs::
  .. code-tab:: go

        api.ListAssets(tenant, zone, app string, activeVm, inactiveVm, activeContainer, inactiveContainer bool, startTime, endTime time.Time)


ListAlerts()
**************

Get alerts

.. tabs::
  .. code-tab:: go

        api.ListAlerts(tenant string, filter *araali_api_service.AlertFilter, count int32, pagingToken string)


ListLinks()
**************

Get links within a zone/app

.. tabs::
  .. code-tab:: go

        api.ListLinks(tenant, zone, app, service string, startTime, endTime time.Time)


ListInsights()
**************

Get tenant wide insights

.. tabs::
  .. code-tab:: go

        api.ListInsights(tenantID, zone string
