Python Backend
==============

.. _analyses_configurations:

Analyses Configurations
-----------------------

Example ``analyses/index.yaml``:

.. literalinclude:: ../databench/analyses_packaged/index.yaml
    :language: yaml

Defaults at the global level for ``index.yaml``:

.. code-block:: none

    title: Databench
    description: null
    description_html: null
    author: null
    version: null
    build: null
    watch: null

    analyses:
      ...


Routes
------

Add a ``routes.py`` file to your analysis with extra Tornado request handlers
and register them in a ``ROUTES`` variable. This is an example of a
``routes.py`` file:

.. literalinclude:: ../databench/tests/analyses/simple2/routes.py
    :language: python


Autoreload and Build
--------------------

Autoreload watches all dependent Python files and rebuilds when any of them
change. It can be deactivated with the command line option ``--no-watch``.
Autoreload uses `tornado.autoreload` in the backend.

To run a single build
(e.g. before deploying a production setting for Databench), use the
``--build`` command line option.


SSL
---

Provide ``--ssl-certfile``, ``--ssl-keyfile`` and ``--ssl-port``.


Command Line and Request Arguments
----------------------------------

Command line parameters are in ``self.cli_args`` and the arguments from the
http request are in ``self.request_args``.

.. versionchanged:: 0.7
