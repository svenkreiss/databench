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


Templates
---------

Modify the ``base.html``, ``analysis.html`` or any other html template file
by placing a ``base.html`` or ``analysis.html`` file in your analyses path.
Use ``analyses/static`` for static assets like logos
and favicons which is exposed at ``/static``.

Default ``analyses/base.html``:

.. literalinclude:: ../databench/templates/base.html
    :language: html

Default ``analyses/analysis.html``:

.. literalinclude:: ../databench/templates/analysis.html
    :language: html


Routes
------

Add a ``routes.py`` file to your analysis with extra Tornado request handlers
and register them in a ``ROUTES`` variable. This is an example of a
``routes.py`` file:

.. literalinclude:: ../databench/tests/analyses/simple2/routes.py
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


Command Line and Request Arguments
----------------------------------

Command line parameters are in ``self.cli_args`` and the arguments from the
http request are in ``self.request_args``.

.. versionchanged:: 0.7


API Reference
-------------

Analysis
~~~~~~~~

.. autoclass:: databench.Analysis


Meta
~~~~

.. autoclass:: databench.Meta
   :members:


Datastore
~~~~~~~~~

.. autoclass:: databench.Datastore
   :members:


Utils
~~~~~

.. autofunction:: databench.utils.fig_to_src
.. autofunction:: databench.utils.png_to_src
.. autofunction:: databench.utils.svg_to_src


Testing
~~~~~~~

.. autoclass:: databench.testing.AnalysisTest
   :members:
