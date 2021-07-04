Contributing
============

This documentation is currently open-source, meaning you can submit pull requests on the GitHub page to change the
documentation.

==================
Installation/Setup
==================

Clone Repo
----------
1. Login into GitHub (or create your account)
2. Setup `ssh <https://github.com/settings/ssh/new>`_ (upload your public key to github account)
3. Fork the `existing repo <https://github.com/araalinetworks/api>`_ (top-right button)
4. Clone the forked repo using ssh (not html)
    - Click the clone button to get repo details for ssh
5. git clone <*repo link from step 4*>
6. Make changes (see :ref:`rst-files`)
7. Push changes
8. Submit pull request
9. Keep fork synced to upstream by following the steps for UI on `this link <https://docs.github.com/en/github/collaborating-with-pull-requests/working-with-forks/syncing-a-fork>`_, then executing the following lines to get the synced-up changes on your laptop::


    git pull -r
    # this line might fail
    # in that case, stash and pop your local changes
    # to make sure the pull goes through
    git stash
    git pull -r
    git stash pop

Install sphinx-doc using your system installer
----------------------------------------------

mac install::

    brew install sphinx-doc

linux install::

    sudo apt-get -y install sphinx-doc

Make sure sphinx-build is in your path
--------------------------------------

Let the installer prompt you for the path. Or see manual instructions below. ::

    cd api/doc
    sudo find / -name sphinx-build -print 2>/dev/null
    export PATH=$PATH:<new_path_where_sphinx-build_is>

*new_path_where_sphinx-build_is* is where you have above sphinx-build

Eg:  ``PATH="/usr/local/opt/sphinx-doc/bin:$PATH`` ::

    cat ~/.zshrc

You can put this in your ``.bashrc`` or ``.zshrc`` so it is automatically set on next login/terminal ::

    source ~/.bashrc

Set up Sphinx with Python
-------------------------

Follow `this link <https://www.docslikecode.com/learn/01-sphinx-python-rtd/>`_ ::

    python3 -m venv ve-name
    # even when you open a new terminal next time, this is how
    # you get into the virtual environment
    source ve-name/bin/activate
    # now all this goes into your virtual env - which is very isolated
    # and predictable environment to be in
    # next time there is no need to install these. Just entering your
    # virtual env gets you all the packages.
    pip install sphinx
    pip install sphinx_rtd_theme

Repeat these steps to see changes in action ::

    make clean html

    To run locally:
        open build/html/index.html

    To run remotely:
        python -m http.server 8000
        In a browser, <ip_of_your_server>:8000



.. _rst-files:

====================
How to Use rST Files
====================

To contribute to the documentation, some knowledge of rST is required. Below are some helpful links.

- `Docutils or reStructuredText <https://docutils.sourceforge.io/rst.html>`_
- `A reStructuredText Primer <https://docutils.sourceforge.io/docs/user/rst/quickstart.html>`_
- `Documenting Your Project Using Sphinx — an_example_pypi_project v0.0.5 documentation <https://pythonhosted.org/an_example_pypi_project/sphinx.html>`_
- `reStructuredText Primer - Sphinx Documentation <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#rst-primer>`_
- `Sphinx Tutorial <https://sphinx-tutorial.readthedocs.io/>`_
- `Sphinx Cheat Sheet <https://sphinx-tutorial.readthedocs.io/cheatsheet/>`_
- `Online reStructuredText Editor <http://rst.ninjs.org/>`_

