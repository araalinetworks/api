Template as Code
================

In order to work with templates from the command line as opposed to
the UI, there are a few commands we can use.

Config
------

The config command is the first command that should be used. It will
specify the Araali user::

    # The <tenant-name> is optional

    # To specify 1 tenant
    ./template.py config -t=<tenant-name>:<tenant-id>

    # To specify multiple tenants
    ./template.py config --tenants=<tenant-name>:<tenant-id>,<tenant-name>:<tenant-id>,<tenant-name>:<tenant-id>,<tenant-name>:<tenant-id>

    # To specify template directory
    ./template.py config -d=<template-directory>

List
----

The list command can be used to list the templates for a tenant::

    # To access local templates
    ./template.py ls -T=<optional-template-name-or-path>

    # To access public templates
    ./template.py ls -p -T=<optional-template-name-or-path>

    # If no template is provided, defaults to all templates

Pull
----

The pull command can be used to make a copy of the public branch template
into your local branch::

    ./template.py pull -p -T=<template-name-or-path>

    # If no template is provided, defaults to all templates

Format
------

The format command is used to apply edits to the template::

    ./template.py fmt <template>

Push
----

The push command is used to push the local branch template to the public branch. **NOTE: This is a dangerous command.**
Only run if you are confident in your changes to the template::

    ./template.py push -p -T=<template-name-or-path>

    # If no template is provided, defaults to all templates

Drift
-----

As edits are made to the templates, the local branch can start to
differ slightly from the public one. The drift command can be used to
check these differences::

    ./template.py drift -p -n -T=<template-name-or-path>

    # If no template is provided, defaults to all templates

Alerts
------
The alerts command can be used to check any alerts::

    ./template.py alerts -n


