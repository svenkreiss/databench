Frontend
========

This is section contains an overview of techniques and best practices that can
be used on the frontend, followed by a short overview of the frontend API and
a subsection on generic UI elements (buttons, sliders, etc).


.. _frontend-overview:

Overview
--------

.. _customization:

Customization (outdated)
++++++++++++++++++++++++

You can customize the header in ``analyses/__init__.py``:

.. code-block:: python

    header_logo = '/analyses_static/logo-header.svg'
    header_title = 'My-awesome-project-or-company-name'

Place the ``logo-header.svg`` file in ``analyses/static/``. Any standard image format like ``.png``, ``.jpeg`` and ``.svg`` is supported.

In the html template, ``[[ analysis_description ]]`` returns the description
string passed into :class:`databench.Analysis` which is usually the ``__doc__``
string of your analysis Python file.


Formatting: Math, Markdown and src Files (outdated)
+++++++++++++++++++++++++++++++++++++++++++++++++++

The frontend also renders math expressions enclosed in ``\\(`` and ``\\)`` as
inline math and as block math when they are enclosed in ``$$`` and ``$$``. It
also renders Markdown when it is enclosed in ``{% filter markdown %}`` and
``{% endfilter %}``. You can also include an external Markdown file with the
``include_md(file)`` macro::

    {% from 'macros.html' import include_md %}
    [[ include_md('helloworld/README.md') ]]

To include an external source code file, use the ``include_src(file, type)``
macro.


Twitter Bootstrap and Font Awesome (outdated)
+++++++++++++++++++++++++++++++++++++++++++++

`Twitter Bootstrap <http://getbootstrap.com/>`_ is
included so that responsive layouts of the form

.. code-block:: html

    <div class="row">
        <div class="col-md-6">First column</div>
        <div class="col-md-6">Second column</div>
    </div>

and many more things work out of the box.
`Font Awesome <http://fortawesome.github.io/Font-Awesome/>`_ is also
included so that you can add icons to your documentation. This also works
within Markdown rendered text. Therefore, you can link to your GitHub project
that hosts the analysis with

.. code-block:: html

    <i class="fa fa-fw fa-github"></i>
    This [analysis is on GitHub](https://github.com/svenkreiss/databench_examples/tree/master/analyses/mpld3pi).

which shows a GitHub icon and the Markdown rendered text with a link.


Static Files (outdated)
+++++++++++++++++++++++

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
to access the files is ``/analyses_static/my_static_file.png``. This is
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


.. _include-databench-js:

Including Databench's JavaScript Library (outdated)
+++++++++++++++++++++++++++++++++++++++++++++++++++

When using the ``base.html`` template, the databench library and a few more
libraries are already loaded:

.. code-block:: html

    <script src="/static/jquery/jquery-2.1.1.min.js"></script>
    <script src="/static/bootstrap-3.1.1-dist/js/bootstrap.min.js"></script>
    <script src="/static/MathJax/MathJax.js?config=TeX-AMS_HTML"></script>
    <script src="/static/d3/d3.v3.min.js"></script>
    <script src="/static/mpld3/mpld3.v0.2.js"></script>
    <script src="/static/databench.js"></script>

When using your own html template, you need to include at least ``jQuery``
and ``databench.js``.


Running the Backend at a Custom Location (outdated)
+++++++++++++++++++++++++++++++++++++++++++++++++++

You can also include Databench in websites. For that, you need the
Databench JavaScript library (explained above at :ref:`include-databench-js`)
and you need to tell the frontend the location of your Databench backend:

.. code-block:: javascript

    var databench = Databench({
        ws_url: 'ws://databench-examples.svenkreiss.com/simplepi/ws',
    });

which connects to the backend of the
`public and live example of simplepi <http://databench-examples.svenkreiss.com/simplepi/>`_.
When you connect to your own backend, you will have to invoke databench with

.. code-block:: bash

    databench --host=0.0.0.0

to allow non-local access.

WARNING: Databench was developed for deployment in trusted environments.
You need to handle security yourself, e.g. by running Databench on an
isolated server.



Databench JavaScript Frontend (outdated)
----------------------------------------

This is the API documentation for the Databench JavaScript library.

.. js:function:: Databench(opts)

    At the heart of this closure are the :js:func:`Databench.emit` and
    :js:func:`Databench.on` functions. Use them in your own JavaScript
    code to communicate with the backend.

    :param opts: Options to customize Databench. `ws_url` changes the
        default url for connecting to the backend. `content_class_name` is
        the CSS class name of the object that wraps the content which is
        used to insert pop-up notifications into the page.

    .. js:function:: Databench.emit(signalName, message)

        :param string signalName: Name of the signal that is used to send the
            message.
        :param message: Message to send.

    .. js:function:: Databench.on(signalName, callback)

        :param string signalName: Name of the signal to listen to from the backend.
        :param function callback: Function that is called when a signal is
            received.

    .. js:attribute:: Databench.genericElements

        A set of generally useful elements that are documented right below.


.. _ui:

UI (partially outdated)
---

Below is the list of genericElements that are in :js:func:`Databench`.
They all can be instantiated from
JavaScript on the frontend. They are also created automatically for the
following elements on the page:

* :js:func:`Databench.genericElements.log`: a ``<pre>`` with an ``id`` starting with ``log``
* :js:func:`Databench.genericElements.mpld3canvas`: a ``<div>`` with an ``id`` starting with ``mpld3canvas``. The exact ``id`` becomes the signal name.
* :js:func:`Databench.genericElements.button`: a ``<button>`` with a ``data-signal-name`` attribute.
* :js:func:`Databench.genericElements.slider`: any ``<input[type='range']>`` element. The ``name`` attribute is used as the signalName.


And here are the genericElements:

.. js:function:: Databench.genericElements.log([id, signalName, limit, consoleFnName])

    :param id: ``id`` of a ``<pre>`` element.
    :param string signalName: The signal to listen for.
    :param int limit: Maximum number of lines to show (default=20).
    :param string consoleFnName: Name of a method of ``console``, like
        'log' (default).

    This function provides log message handling from the frontend and
    backend. By default, this looks at ``log`` messages from the backend and at
    ``console.log()`` calls on the frontend. All messages will be shown in the
    bound ``<pre>`` element and in the browser console. When no ``id`` is given, it will only show the messages in the browser console.

.. js:function:: Databench.ui.Button(node)

    :param node: a document node (e.g. returned by ``document.getElementById('id_of_node')``).

    The signalName can be extracted from an attribute ``data-signal-name``
    and an optional message can be provided in JSON format in ``data-message``.
    The signalName and the message are used for a :js:func:`Databench.emit`.

    This function adds actions to an HTML button. It adds a ``click`` event
    handler and tracks the status of the action through the backend. The button
    is set to active (the CSS class ``active`` is added) during the execution
    in the backend.

    :js:func:`wire`:
    Wires all buttons that have a ``data-signal`` attribute.
    If the element also has a ``data-message`` attribute formatted in JSON,
    it will be send with the signals.

    **Example**: ``index.html``:

    .. code-block:: html

        <button data-signal="run">Run</button>

    In ``analysis.py``, add

    .. code-block:: python

        def on_run(self):
            """Run when button is pressed."""
            pass

    to the ``Analysis`` class. In this form, Databench finds the button
    automatically and connects it to the backend. No additional JavaScript
    code is required.

.. js:function:: Databench.genericElements.slider(selector[, signalName])

    :param selector: ``id`` or jQuery selector of an ``<input[type='range']>``
        element.
    :param string signalName: if not provided, it is taken from a
        ``data-signal-name``, if that does not exist then from the ``name``
        attribute and if that is also not given then it
        is set to the id.

    The signalName can be extracted from an attribute ``data-signal-name`` or
    ``name`` (which is more natural for ``<input>`` elements).
    The signalName is used for :js:func:`Databench.emit` and the message is
    an array only containing the value of the slider.

    **Example**: ``index.html``:

    .. code-block:: html

        <label for="samples">Samples:</label>
        <input type="range" name="samples" value="1000"
            min="100" max="10000" step="100" />

    In ``analysis.py``, add

    .. code-block:: python

        def on_samples(self, value):
            """Sets the number of samples to generate per run."""
            self.samples = value

    to the ``Analysis`` class. In this form, Databench finds the slider
    automatically and connects it to the backend. No additional JavaScript
    code is required.
