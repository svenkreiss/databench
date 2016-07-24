Frontend
========

This is section contains an overview of techniques and best practices that can
be used on the frontend, followed by a short overview of the frontend API and
a section on UI elements (buttons, text boxes, sliders, etc).


.. _frontend-overview:

Overview
--------

Additional Views
++++++++++++++++

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



HTML Template
+++++++++++++

Templates are rendered buy Tornado's template engine. Databench provides
a visual frame for your analysis which you can extend from with
``{% extends "analysis.html" %}``.
This template offers you three main entry points for modifying the HTML page.
Those are the template blocks ``head`` which places your code inside the
HTML ``<head>``, ``analysis`` which inserts your main code into the
HTML ``<body>`` and ``footer`` for code that should be placed right before the
closing ``</body>`` tag.

Here is an example for making use of the ``head`` block:

.. code-block:: html

    {% block head %}
        <!-- Add inline CSS to the page: -->
        <style>p { font-family: serif; }</style>

        <!-- Add a css file (put my-style.css into analyses/scaffold/): -->
        <link rel="stylesheet" type="text/css" href="/static/my-style.css">
    {% end %}


Extensions
++++++++++

Databench is supposed to go out of your way and work well with many
frontend frameworks and tools. For example, it works well with Twitter
Bootstrap, Font Awesome, MathJax, and many more.



Static Files
++++++++++++

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
see :ref:`customization`.


Node Modules
++++++++++++

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
++++++++++++++++++++++++++++++++++++++++

You can also include Databench in websites. You need the Databench JavaScript
library and configure the location of your Databench backend:

.. code-block:: javascript

    var d = Databench.Connection(
        null,
        'ws://databench-examples.trivial.io/simplepi/ws',
    );

which connects to the backend of the `public and live example of simplepi`_.
When you connect to your own backend, you will have to invoke databench with

.. code-block:: bash

    databench --host=0.0.0.0

to allow non-local access.

WARNING: Databench was developed for deployment in trusted environments.
You need to handle security yourself, e.g. by running Databench on an
isolated server.


.. _frontend-api:

JavaScript API
--------------

``databench.js`` is exposed at ``/_static/databench.js``. Please see the
`complete JS API reference`_.

.. _`angular analysis in the Databench examples`: https://github.com/svenkreiss/databench_examples/tree/master/analyses/angular
.. _`databench_examples repository`: https://github.com/svenkreiss/databench_examples/
.. _`complete JS API reference`: http://www.svenkreiss.com/databench/
.. _`public and live example of simplepi`: http://databench-examples.trivial.io/simplepi/
