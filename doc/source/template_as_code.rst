Template as Code
================

In order to work with templates from the command line as opposed to
the UI, there are a few commands we can use. Before you get started,
make sure you are in the Python directory, and run::

    ./setup.sh
    
Commands
********

Config
------

The config command is the first command that should be used. It will
specify the git directory::

    # To specify directory for git
    ./template.py config -d=<git-directory>

List
----

The list command can be used to list the templates for a tenant::

    # To access local templates
    ./template.py ls

    # To access public templates
    ./template.py ls -p

Pull
----

The pull command can be used to make a copy of the public branch template
into your local branch::

    ./template.py pull -p -T=<template-name-or-path>

    # If no template is provided, defaults to all templates

Format
------

The format command is used to apply edits to the template::

    ./template.py fmt <template-path>

Push
----

The push command is used to push the local branch template to the public branch. **NOTE: This is a dangerous command.**
Only run if you are confident in your changes to the template::

    ./template.py push -T=<template-name-or-path>

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

    ./template.py alerts


Example Videos
**************

Updating a Docker Template
--------------------------

.. raw:: html

   <script id="asciicast-De3oYu2yjoZL5TYSxlCoxwsSv" src="https://asciinema.org/a/De3oYu2yjoZL5TYSxlCoxwsSv.js" async></script>

Adding a New Link from UI to git
--------------------------------

.. raw:: html

   <script id="asciicast-haEeqegDMT1cwWTpJb0KYHCX6" src="https://asciinema.org/a/haEeqegDMT1cwWTpJb0KYHCX6.js" async></script>