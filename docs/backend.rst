Python Backend
==============

A single analysis can be run programmatically from Python using :func:`databench.run`.


.. _analyses_configurations:

Multiple Analyses Configuration
-------------------------------

Example ``analyses/index.yaml`` file:

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


.. _backend_logging:

Logging
-------

Use Python's `logging` as usual. To log to `logging` and
send a message to the frontend about the log message, use
``self.emit('log', ...)``. Similarly, if the frontend emits a ``log`` action,
a backend `logging` message will also be emitted. Similarly to
``log``, this also works for ``warn`` and ``error``.
Also see :ref:`frontend_logging` in the JavaScript section.


Routes
------

Add to the ``static`` map in ``index.yaml`` to serve static files. The ``static``
map is a regular expression to match the url against which contains a single capture
bracket and the root folder. In this example configuration

.. code-block:: yaml

    static:
      static/(.*): folder_with_static_files/

any url starting with ``static/`` followed by any character sequence ``.*`` which is
captured by the surrounding ``()`` is matched to that file in ``folder_with_static_files/``.

For more specialized routes, add a ``routes.py`` file to your analysis with extra
`tornado.web.RequestHandler` s
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

Command line parameters are in available in `.Analysis` instances as
``self.cli_args`` and the arguments from the
http request are in ``self.request_args``.
