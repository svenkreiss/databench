Frontend
========

This is section contains an overview of techniques and best practices that can
be used on the frontend, followed by a short overview of the frontend API and
a section on UI elements (buttons, text boxes, sliders, etc).


.. _frontend-overview:

Overview
--------

.. _customization:

Customization
+++++++++++++

You can customize the header in ``analyses/README.md``:

.. code-block:: markdown

    title: Databench - Packaged Analyses
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
        d.connect();

        d.on('ready', function(data) {
            console.log(`Ready message received: ${data}`);
        });
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
        <link rel="stylesheet" type="text/css" href="static/my-style.css">
    {% end %}


Extensions
++++++++++

Math with MathJax, Twitter Bootstrap, Font Awesome and many more work together
well with Databench in the frontend.



Static Files
++++++++++++

To add a static file to an analysis, place it in the analysis folder. Static
files in this folder are exposed at the ``/<some_analysis>/static/`` url.
For example, to add ``angular.js`` to an analysis of the name *angular*
(see for example the `angular analysis in the Databench examples <https://github.com/svenkreiss/databench_examples/tree/master/analyses/angular>`_), add the
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

Put inside of ``analyses`` folder.

.. code-block:: bash

    cd analyses
    npm init  # creates package.json interactively
    npm install --save d3  # install d3 and add as dependency to packages.json

to then access it with

.. code-block:: html

    <script src="/node_modules/d3/d3.min.js"></script>

in html. You can check that JavaScript file into your version control
or require users to run ``cd analyses; npm install`` to install their own
``node_modules`` locally.


Running the Backend at a Custom Location
++++++++++++++++++++++++++++++++++++++++

You can also include Databench in websites. You need the Databench JavaScript
library and configure the location of your Databench backend:

.. code-block:: javascript

    var d = Databench.Connection(
        null,
        'ws://databench-examples.trivial.io/simplepi/ws',
    );

which connects to the backend of the
`public and live example of simplepi <http://databench-examples.trivial.io/simplepi/>`_.
When you connect to your own backend, you will have to invoke databench with

.. code-block:: bash

    databench --host=0.0.0.0

to allow non-local access.

WARNING: Databench was developed for deployment in trusted environments.
You need to handle security yourself, e.g. by running Databench on an
isolated server.



Databench JavaScript Frontend Library
-------------------------------------

This is the API documentation for ``databench.js``.

.. js:function:: Databench.Connection(analysis_id=null, ws_url=null)

    At the heart of this class are the :js:func:`Databench.Connection.emit` and
    :js:func:`Databench.Connection.on` functions. Use them in your own
    JavaScript code to communicate with the backend.

    :param string analysis_id:
        Sets an analysis id. The connection will try to connect to a previously
        created analysis with that id.

    :param string ws_url:
        Sets the url of the backend. If ``null`` (default) the location is
        inferred automatically.

    .. js:function:: Databench.emit(action, data)

        :param string action:
            Name of an action that is sent to the backend.
        :param data:
            Data associated with the action.

    .. js:function:: Databench.on(signal, callback)

        :param signal:
            An Object of the form ``{data: status}`` to listen for updates of
            the ``status`` entry in the ``data`` Datastore.
            It can also be the name of the signal to listen to from the
            backend but this should only be used for lower level functionality.

        :param function callback:
            Function that is called when a matching signal is received.


.. _ui:

User Interface (UI)
-------------------

Below is the list of :js:func:`Databench.UIElements` that are in
:js:func:`Databench`. The DOM nodes are "wired" manually or using
:js:func:`Databench.ui.wire`.

* :js:class:`Databench.ui.Log`: node (usually a ``<pre>``) with ``id="log"``
* :js:class:`Databench.ui.StatusLog`: node (usually a ``<div>``) with ``id="ws-alerts"``
* :js:class:`Databench.ui.Button`: a ``<button>`` with an action name
* :js:class:`Databench.ui.Text`: a ``<span>``, ``<p>``, ``<div>``, ``<i>`` or ``<b>`` with an action name
* :js:class:`Databench.ui.TextInput`: a ``<input[type='text']>`` with an action name
* :js:class:`Databench.ui.Slider`: a ``<input[type='range']>`` with an action name

Action names are determined from ``name`` or ``data-action`` attributes.


.. js:class:: Databench.UIElement(node)

    :param node: DOM element

    Adds ``databench_ui`` to the DOM element with the UIElement that
    wired this node.


    .. js:attribute:: action_name

        Name of the action for this element. A default name is determined from
        the DOM ``data-action`` attribute or from the ``name`` attribute and
        can be overwritten.

    .. js:function:: action_format(value)

        :param value: value of the element
        :returns: a formatted message for an action

        Overwrite this function to implement custom behavior.

    .. js:attribute:: wire_signal

        The default is ``{data: <action_name>}``. This can be changed.


.. js:function:: Databench.ui.wire(connection)

    Wires all elements. Skips elements containing ``data-skipwire="true"``.


And here are the UI elements:

.. js:class:: Databench.ui.Log(node, consoleFnName='log', limit=20, length_limit=250)

    :param node: DOM element
    :param string consoleFnName: name of a method of ``console``
    :param int limit: maximum number of lines to show
    :param int length_limit: maximum number of characters per line

    .. js:function:: add(message, source='unknown')

        adds a message and marks it from the given source


.. js:class:: Databench.ui.StatusLog(node, formatter=StatusLog.default_alert)

    :param node: DOM element
    :param formatter: a function taking a message and a count of that message and returning an HTML string

    .. js:function:: add(msg)

        add a message


.. js:class:: Databench.ui.Button(node)

    :param node: DOM element

    This function adds actions to an HTML button. It adds a ``click`` event
    handler and tracks the status of the process through the backend. The button
    is set to active (the CSS class ``active`` is added) during the execution
    on the backend.


    **Example**: ``index.html``:

    .. code-block:: html

        <button data-action="run">Run</button>

    In ``analysis.py``, add

    .. code-block:: python

        def on_run(self):
            """Run when button is pressed."""
            pass

    to the ``Analysis`` class. In this form, Databench finds the button
    automatically and connects it to the backend. No additional JavaScript
    code is required.


.. js:class:: Databench.ui.Text(node)

    :param node: DOM element

    .. js:attribute:: format_fn

        overwrite this variable with a function that maps a signal to the
        text that should be shown


.. js:class:: Databench.ui.TextInput(node)

    :param node: an ``<input>`` DOM element with ``type="text"``

    .. js:attribute:: format_fn

        overwrite this variable with a function that maps a signal to the
        text that should be shown


.. js:class:: Databench.ui.Slider(node, label_node)

    :param node: an ``<input>`` DOM element with ``type="range"``
    :param label_node: a corresponding ``<label>`` DOM element

    **Example**: ``index.html``:

    .. code-block:: html

        <label for="samples">Samples:</label>
        <input type="range" name="samples" value="1000"
            min="100" max="10000" step="100" />

    In ``analysis.py``, add

    .. code-block:: python

        def on_samples(self, value):
            """Sets the number of samples to generate per run."""
            self.data['samples'] = value

    to the ``Analysis`` class. The Python code is for illustration only and can
    be left out as assigning the ``value`` to the key with the name of the
    action in ``self.data`` is the default behavior.
