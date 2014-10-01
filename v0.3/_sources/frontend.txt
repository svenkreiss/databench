Frontend
========

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

You can customize the header in ``analyses/__init__.py``:

.. code-block:: python

    header_logo = '/analyses_static/logo-header.svg'
    header_title = 'My-awesome-project-or-company-name'

Place the ``logo-header.svg`` file in ``analyses/static/``. Any standard image format like ``.png``, ``.jpeg`` and ``.svg`` is supported.

In the html template, ``[[ analysis_description ]]`` returns the description
string passed into :class:`databench.Analysis` which is usually the ``__doc__``
string of your analysis Python file.

The frontend also renders math expressions enclosed in ``\\(`` and ``\\)`` as
inline math and as block math when they are enclosed in ``$$`` and ``$$``. It
also renders Markdown when it is enclosed in ``{% filter markdown %}`` and
``{% endfilter %}``. You can also include an external Markdown file with the
``include_md(file)`` macro::

    {% from 'macros.html' import include_md %}
    [[ include_md('helloworld/README.md') ]]

To include an external source code file, use the ``include_src(file, type)``
macro.

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


Databench JavaScript Frontend
-----------------------------

.. js:function:: Databench()

    At the heart of this closure are the :js:func:`Databench.emit` and
    :js:func:`Databench.on` functions. Use them in your own JavaScript
    code to communicate with the backend.

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


.. _genericElements:

Generic Elements
----------------

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

.. js:function:: Databench.genericElements.mpld3canvas(id[, signalName])

    :param id: ``id`` of the element.
    :param string signalName: Waiting for plots to be send on this signal
        (default='mpld3canvas').

.. js:function:: Databench.genericElements.button(selector[, signalName])

    :param selector: ``id`` or jQuery selector of a ``button`` element.
    :param string signalName: if not provided, it is taken from a
        ``data-signal-name`` attribute and if that is also not given then it
        is set to the id.

    The signalName can be extracted from an attribute ``data-signal-name``
    and an optional message can be provided in JSON format in ``data-message``.
    The signalName and the message are used for a :js:func:`Databench.emit`.

    This function adds actions to an HTML button. It adds a ``click`` event
    handler and tracks the status of the action through the backend. The button
    is set to active (the CSS class ``active`` is added) during the execution
    in the backend.

    **Example**: ``index.html``:

    .. code-block:: html

        <button class="btn btn-primary" data-signal-name="run">Run</button>

    where ``class="btn btn-primary"`` is only added to make the button look
    nicer via `Twitter Bootstrap Buttons <http://getbootstrap.com/css/#buttons>`_. In ``analysis.py``, add

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
