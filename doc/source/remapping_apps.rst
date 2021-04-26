Remapping Apps
==============
Araali uses convention to discovers apps in your k8s environment. As best
practice, apps are deployed in their own namespace. There is no good reason to
actually not do so.

However, due to team isolation, sometimes namespaces are pre-created by the
infrastructure team and kept small by design (to prevent proliferation and also
to keep the privileges for namespace management limited to a smaller team).

For e.g. some people could have static namespaces that denote environments
instead of apps (prod, staging, dev). In other cases, namespaces could be
created per team for isolation (team1, team2). If teams map to features/apps,
then there is not much of an issue. However, a single team could be responsible
for multiple logical apps and the namespace itself ends up becoming a container
for these apps.

For such scenarios Araali allows you to customize apps the way you understand
it, regardless of which namespace they will show up in.

App mapping by example
----------------------
This is a sample google shop application where all the pods show up under a
single app - gshop. We’ll walk through the process of splitting this up into
three different apps.

.. image:: images/before-app-remapping.png
 :alt: Before remapping apps

List all the apps to pod mapping as a yaml file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

        $ ./araalictl api -list-pod-mappings > pod_mapping.yaml

Update the mapping yaml file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        i. We delete the pods we don’t want to remap.
        ii. As we can see we have the app and namespace set to the same value.
        iii. Now we reset the app to the name we would like to see it as.

This can be done programmatically as well. Here we show a manual way of editing
the yaml files.

Below is a sample yaml file generated. Now we would like to re-map the pods as
below.

        frontend → gshop-frontend

        redis-cart → gshop-db

        rest of the services → gshop-service

::

        $ vi pod_mapping.yaml
        - zone: prod
          namespace: gshop
          pod: checkoutservice
          app: gshop
        - zone: prod
          namespace: gshop
          pod: frontend
          app: gshop
        - zone: prod
          namespace: gshop
          pod: cartservice
          app: gshop
        - zone: prod
          namespace: gshop
          pod: recommendationservice
          app: gshop
        - zone: prod
          namespace: gshop
          pod: currencyservice
          app: gshop
        - zone: prod
          namespace: gshop
          pod: shippingservice
          app: gshop
        - zone: prod
          namespace: gshop
          pod: adservice
          app: gshop
        - zone: prod
          namespace: gshop
          pod: redis-cart
          app: gshop
        - zone: prod
          namespace: gshop
          pod: productcatalogservice
          app: gshop
        - zone: prod
          namespace: gshop
          pod: emailservice
          app: gshop
        - zone: prod
          namespace: gshop
          pod: paymentservice
          app: gshop

Edited yaml file (with changed app)::

        $ vi pod_mapping.yaml
        - zone: prod
          namespace: gshop
          pod: checkoutservice
          app: gshop-service
        - zone: prod
          namespace: gshop
          pod: frontend
          app: gshop-frontend
        - zone: prod
          namespace: gshop
          pod: cartservice
          app: gshop-service
        - zone: prod
          namespace: gshop
          pod: recommendationservice
          app: gshop-service
        - zone: prod
          namespace: gshop
          pod: currencyservice
          app: gshop-service
        - zone: prod
          namespace: gshop
          pod: shippingservice
          app: gshop-service
        - zone: prod
          namespace: gshop
          pod: adservice
          app: gshop-service
        - zone: prod
          namespace: gshop
          pod: redis-cart
          app: gshop-db
        - zone: prod
          namespace: gshop
          pod: productcatalogservice
          app: gshop-service
        - zone: prod
          namespace: gshop
          pod: emailservice
          app: gshop-service
        - zone: prod
          namespace: gshop
          pod: paymentservice
          app: gshop-service

Update the pod to app mapping in araali
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

        $ cat pod_mapping.yaml | ./araalictl api -update-pod-mappings

Once the above exercise is complete we can see that a single app before got
split into three different apps as below.

.. image:: images/after-app-remapping.png
 :alt: After remapping apps


Programmatic mapping example
----------------------------
This can also be programmatically achieved using our python APIs. The
transformations should ideally be idempotent so they can be rerun without
issues::

        mapping = araalictl.get_pod_apps()

        if (obj["zone"] == "nightly-k8s" and 
            obj["namespace"] == "nightly-bend" and 
            "pod" in obj):

            if obj["pod"] in ["flowstitcher", "flowprocessor",
                              "assetinfo-processor",
                              'applens-generator', 
                              "applens-compactor", 
                              "vulnscanner"]:

                obj["app"] = "nightly-bend-pipeline"

        araalictl.push_pod_apps(mapping)
