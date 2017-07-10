JavaScript Frontend
===================

This is section contains an overview of techniques and best practices that can
be used on the frontend, followed by a short overview of the frontend API and
a section on UI elements (buttons, text boxes, sliders, etc).


.. _frontend-overview:

Additional Views
----------------

Next to the ``index.html``, you can create other html files like this
``log.html`` file:

.. code-block:: html

    {% extends "analysis.html" %}


    {% block footer %}
    <script>
        var d = new Databench.Connection();
        Databench.ui.wire(d);

        d.on('ready', function(data) {
            console.log(`Ready message received: ${data}`);
        });

        d.connect();
    </script>
    {% end %}

which will automatically be available at the url ending with ``log.html``.



HTML Templates
--------------

Templates are rendered buy Tornado's template engine. Databench provides
a visual frame for your analysis which you can extend from with
``{% extends "analysis.html" %}``. Example:

.. literalinclude:: ../databench/analyses_packaged/scaffold/index.html
    :language: html

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


Extensions
----------

Databench is supposed to go out of your way and work well with many
frontend frameworks and tools. For example, it works well with Twitter
Bootstrap, React, Font Awesome, MathJax, and many more.


.. _frontend_logging:

Logging
-------

.. versionchanged:: 0.7

Use ``console.log()`` to log to the console as usual. To log to the console and
send a message to the backend about the log message, use
``d.emit('log', ...)``. Similarly, if the backend emits a ``log`` action, the
frontend console as well as ``databench.ui.Log`` will show it. Similarly to
``log``, this also works for ``warn`` and ``error``.
Also see :ref:`backend_logging` in the Python section.


Static Files
------------

To add a static file to an analysis, place it in the analysis folder. Static
files in this folder are exposed at the ``/<some_analysis>/static/`` url.
For example, to add ``angular.js`` to an analysis of the name *angular*
(see for example the `angular analysis in the Databench examples`_), add the
file ``angular.js`` to the folder ``analyses/angular/`` and include it in
``index.html`` with:

.. code-block:: html

    <script src="/angular/static/angular.js"></script>

You can also add static files to *all* analyses by creating a folder
``analyses/static`` and placing the static file in this folder. The URL
to access the files is ``/static/my_static_file.png``. This is
the same folder that is used for a custom header logo;
see :ref:`analyses_configurations`.


Node Modules
------------

Databench looks for a ``static`` and a ``node_modules`` folder first in the
analyses folder and then in the current working directory.

.. code-block:: bash

    npm init  # creates package.json interactively
    npm install --save d3  # install d3 and add as dependency to packages.json

to then access it with

.. code-block:: html

    <script src="/node_modules/d3/d3.min.js"></script>

in html. The `databench_examples repository`_ contains analyses that use
static files and Node packages.


Running the Backend at a Custom Location
----------------------------------------

You can also include Databench in websites. You need the Databench JavaScript
library and configure the location of your Databench backend:

.. code-block:: javascript

    var d = Databench.Connection('ws://databench-examples.trivial.io/simplepi/ws');

which connects to the backend of the `public and live example of simplepi`_.
When you connect to your own backend, you will have to invoke databench with

.. code-block:: bash

    databench --host=0.0.0.0

to allow non-local access.

WARNING: Databench was developed for deployment in trusted environments.
You need to handle security yourself, e.g. by running Databench on an
isolated server.

.. _`angular analysis in the Databench examples`: https://github.com/svenkreiss/databench_examples/tree/master/analyses/angular
.. _`databench_examples repository`: https://github.com/svenkreiss/databench_examples/
.. _`public and live example of simplepi`: http://databench-examples.trivial.io/simplepi/
