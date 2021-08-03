Notebook Doc
============
Araali creates per app diagrams out of the box. These are not just diagrams,
they actually represent policies that have been automatically figured out for
you. All that is needed of you is review. Once reviewed, the diagrams are
natively enforced by our purpose built firewall.

The policy is represented as a link DB, and you can do data science on these
links. This is quite useful as you tinker around with what Araali has
discovered. The same APIs can be run outside of the notebook as a regular
program/script.

Getting started
---------------

In a terminal::

        # Create a directory where you will checkout from github
        mkdir -p opensrc
        cd opensrc
        git clone git@github.com:araalinetworks/api.git

        # now run the notebook
        cd api/python/
        ./run.sh
   
Accessing Notebook
------------------
To access the notebook, copy and paste this URL into your browser:

        http://localhost:8888/notebooks/araali_api_lens.ipynb

::

        NOTE: Locate token to use in the terminal output

Plain old scripting
-------------------
If you are not familiar with notebook, you can also write old style scripts::

        $ source araali/bin/activate && python3 myscript.py
        $ cat myscript.py

          import api
          import araalictl
          print(api.Lens.monitor_world())

Documentation
-------------
Use the python tab in this guide:

        https://araali-networks-api.readthedocs.io/en/latest/guide_lenses.html
