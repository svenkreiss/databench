.. image:: http://www.svenkreiss.com/databench/logo.svg
    :target: http://www.svenkreiss.com/databench/v0.3/

Databench
=========

    Data analysis tool using Flask, WebSockets and d3.js. Live demos are at
    `databench-examples.svenkreiss.com <http://databench-examples.svenkreiss.com>`_.

.. image:: https://travis-ci.org/svenkreiss/databench.png?branch=master
    :target: https://travis-ci.org/svenkreiss/databench


Documentation
-------------

User guide and API documentation: `www.svenkreiss.com/databench/v0.3/ <http://www.svenkreiss.com/databench/v0.3/>`_


License
-------

Databench was written by Sven Kreiss and made available under the `MIT license <https://github.com/svenkreiss/databench/blob/master/LICENSE>`_.


Changelog
---------

* `master <https://github.com/svenkreiss/databench/compare/v0.2.15...master>`_ (for 0.3.0)
    * ``include_md()`` macro for frontend to include Markdown files
    * python 2.6 support (in addition to 2.7)
    * new tool ``scaffold-databench``
    * moved from socket.io to plain websockets
    * one analysis instance per websocket connection
    * restructured analyses directories
    * signals are executed in separate co-routines
    * interface to other backends using ``zmq``
    * frontend: genericElements take string ids instead of jquery selectors
    * frontend: Databench() does not require a name anymore
    * frontend: genericElements: added ``button()`` and ``slider()``
    * backend handles ``action`` : an ``action`` is the co-routine that is launched with a signal. An ``action`` can have an ``id`` in which case it signals ``start`` and ``end`` (used to indicate state for genericElements.button()).
* `0.2.15 <https://github.com/svenkreiss/databench/releases/tag/v0.2.15>`_ (2014-09-06)
