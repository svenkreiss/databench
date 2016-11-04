Backend
=======

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
    logo_url: /_static/logo.svg
    favicon_url: /_static/favicon.ico
    footer_html: null
    injection_head: ''
    injection_footer: ''
    build: null
    watch: null

    analyses:
      ...

The entries ``injection_head`` and ``injection_footer`` can be overwritten by
placing a ``head.html`` and ``footer.html`` in the analysis folder. This can
be used to insert analytics tracking code.

Examples for customization:

.. code-block:: none

    title: Databench - Packaged Analyses
    description: my awesome analyses
    logo_url: /static/logo-header.svg
    favicon_url: /static/myfavicon.ico
    footer_html: Created by <a href="http://www.trivial.io">me</a>.

Place the ``logo-header.svg`` file in ``analyses/static/``. Any standard image
format like ``.png``, ``.jpeg`` and ``.svg`` is supported.

To modify the style globally (including the index page with the list of
analysis) and to add a tracking snippet for analytics,
you can inject code into the head and the bottom of the page.
Inject code into the ``<head>`` section by creating a ``head.html`` file inside
the analysis folder. Similarly, inject code into the bottom of the ``<body>``
with a ``footer.html`` file.


Routes
------

Add a ``routes.py`` file to your analysis with extra Tornado request handlers
and register them in a ``ROUTES`` variable. This is an example of a
``routes.py`` file:

.. literalinclude:: ../tests/analyses/simple2/routes.py
    :language: python


Autoreload
----------

Uses http://www.tornadoweb.org/en/stable/autoreload.html in the backend which
is only activated Databench is run with ``--log INFO`` or ``--log DEBUG``.

To run a single build (i.e. before deploying a production setting for
Databench), use the ``--build`` command line option.


SSL
---

Provide ``--ssl-certfile``, ``--ssl-keyfile`` and ``--ssl-port``.


Analysis
--------

.. autoclass:: databench.Analysis


Meta
----

.. autoclass:: databench.Meta
   :members:


Datastore
---------

.. autoclass:: databench.Datastore
   :members:


Utils
-----

.. autofunction:: databench.fig_to_src
.. autofunction:: databench.png_to_src
.. autofunction:: databench.svg_to_src


testing
-------

.. autoclass:: databench.testing.AnalysisTestCase
   :members:

.. autoclass:: databench.testing.AnalysisTestCaseSSL
   :members:

.. autoclass:: databench.testing.Connection
   :members:
