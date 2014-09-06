Frontend API
============

When using the ``base.html`` template, the databench library and a few more
libraries are already loaded. When using your own html template, the frontend
library needs to be loaded by including

.. code-block:: html

    <script src="/static/databench.js"></script>

in the html body tag.

In the html template, ``[[ analysis_description ]]`` returns the description
string passed into :class:`databench.Analysis` which is usually the ``__doc__``
string of your analysis python file.


Databench
---------

.. js:class:: Databench()

.. js:attribute:: Databench.genericElements

    :ref:`genericElements` are documented below.

.. js:function:: Databench.emit(signalName, message)

    :param string signalName: Name of the signal that is used to send the
        message.
    :param message: Message to send.

.. js:function:: Databench.on(signalName, callback)

    :param string signalName: Name of the signal to listen to from the backend.
    :param function callback: Function that is called when a signal is received.


.. _genericElements:

Generic Elements
----------------

Below is the list of genericElements. They all can be instantiated from JavaScript on the frontend. They are also created for the following elements on the page:

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
