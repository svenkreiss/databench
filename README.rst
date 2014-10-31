.. image:: http://www.svenkreiss.com/databench/logo.svg
    :target: http://www.svenkreiss.com/databench/v0.3/

Databench
=========

    Data analysis tool using Flask, WebSockets and d3.js. Live demos are at
    `databench-examples.svenkreiss.com <http://databench-examples.svenkreiss.com>`_.

.. image:: https://travis-ci.org/svenkreiss/databench.png?branch=master
    :target: https://travis-ci.org/svenkreiss/databench
.. image:: https://coveralls.io/repos/svenkreiss/databench/badge.png
    :target: https://coveralls.io/r/svenkreiss/databench
.. image:: https://pypip.in/v/databench/badge.svg
    :target: https://pypi.python.org/pypi/databench/
.. image:: https://pypip.in/d/databench/badge.svg
    :target: https://pypi.python.org/pypi/databench/


Documentation and License
-------------------------

| `Tutorial, user guide and API documentation <http://www.svenkreiss.com/databench/v0.3/>`_.
| Databench was written by Sven Kreiss and made available under the `MIT license <https://github.com/svenkreiss/databench/blob/master/LICENSE>`_.


Changelog
---------

* `master <https://github.com/svenkreiss/databench/compare/v0.3.9...master>`_
* `0.3.9 <https://github.com/svenkreiss/databench/compare/v0.3.7...v0.3.9>`_ (2014-10-30)
    * fix analyses/static search path
    * fix included font-awesome
* `0.3.7 <https://github.com/svenkreiss/databench/compare/v0.3.6...v0.3.7>`_ (2014-10-24)
    * improved scaffold with more comments
    * alternative frontends: apart from index.html, now you can also create anything.html and it will be rendered
    * frontend options: connect to a non-standard backend location
    * fix for Windows compatibility
    * wider zeromq compatibility (not using unbind() anymore)
    * CircleCI tests now running
    * docs updated with new features
* `0.3.6 <https://github.com/svenkreiss/databench/compare/v0.3.4...v0.3.6>`_ (2014-10-20)
    * add section on making a plot with d3.js to tutorial
    * improve doc section on frontend
    * add more comments to scaffold
* `0.3.4 <https://github.com/svenkreiss/databench/compare/v0.3.3...v0.3.4>`_ (2014-10-17)
    * added a tutorial to the docs
    * added comments and explanation to scaffold analysis
    * friendlier logo
* `0.3.3 <https://github.com/svenkreiss/databench/compare/v0.3.0...v0.3.3>`_ (2014-10-01)
    * clean up of Python source distribution
    * customizable header
    * serve static files at ``analyses/static/`` under ``analyses_static/``
* `0.3.0 <https://github.com/svenkreiss/databench/compare/v0.2.15...v0.3.0>`_ (2014-09-20)
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
