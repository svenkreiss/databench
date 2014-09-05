Databench
=========

    Data analysis tool using Flask, WebSockets and d3.js. Live demos are at
    `databench-examples.svenkreiss.com <http://databench-examples.svenkreiss.com>`_.

.. image:: https://travis-ci.org/svenkreiss/databench.png?branch=master
    :target: https://travis-ci.org/svenkreiss/databench


Documentation
-------------

User guide and API documentation: `www.svenkreiss.com/databench/ <http://www.svenkreiss.com/databench/>`_


License
-------

Databench was written by Sven Kreiss and made available under the `MIT license <https://github.com/svenkreiss/databench/blob/master/LICENSE>`_.


Changelog
---------

**0.3.0**

* new tool ``scaffold-databench``
* moved from socket.io to plain websockets
* one analysis instance per websocket connection
* restructured analyses directories
* signals are executed in separate co-routines
* interface to other backends using ``zmq``
* frontend: genericElements take string ids instead of jquery selectors
* frontend: Databench() does not require a name anymore
* frontend: genericElements: added ``button()`` and ``slider()``
* backend handles ``action``s: an ``action`` is the co-routine that is launched with a signal. ``action``s can have ``id``s in which case they signal their ``start`` and ``end`` (used to indicate state for genericElements.button()).
