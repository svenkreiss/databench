Frontend API
============

When using the ``base.html`` template, the databench library and a few more
libraries are already loaded. When using your own html template, the frontend
library with the Socket.IO dependency are loaded by including

.. code-block:: html

    <script src="/static/socket.io/socket.io.min.js"></script>
    <script src="/static/databench.js"></script>

in the html body tag.


Databench
---------

.. js:class:: Databench(name)

    :param string name: The name of this databench analysis (used as Socket.IO
        namepsace and has to match the backend's :class:`databench.Analysis`
        ``name``)

.. js:attribute:: Databench.signals
.. js:attribute:: Databench.genericElements


Signals
-------

.. js:function:: Databench.signals.emit(signalName, message)

    :param string signalName: Name of the signal that is used to send the
        message.
    :param message: Message to send.

.. js:function:: Databench.signals.on(signalName, callback)

    :param string signalName: Name of the signal to listen to from the backend.
    :param function callback: Function that is called when a signal is received.


Generic Elements
----------------

.. js:function:: Databench.genericElements.log(selector[, signal_name, limit, console_fn_name])

    This function converts a generic ``<pre>`` element into a basic console. By
    default, this looks at ``log`` messages from the backend and at
    ``console.log()`` calls on the frontend. All messages will be shown in the
    bound ``<pre>`` element and in the browser console.

    :param selector: A jQuery selector.
    :param string signal_name: The signal to listen for.
    :param int limit: Maximum number of lines to show (default=20).
    :param string console_fn_name: Name of a method of console, like
        'log' (default).

.. js:function:: Databench.genericElements.mpld3canvas(selector[, signalName])

    :param selector: A jQuery selector.
    :param string signalName: Waiting for plots to be send on this signal
        (default='mpld3canvas').

