.. image:: http://www.svenkreiss.com/databench/logo.svg
    :target: http://databench.trivial.io

Databench
=========

    Data analysis tool using Tornado and WebSockets. Live demos are at
    `databench-examples.trivial.io <http://databench-examples.trivial.io>`_.

.. image:: https://travis-ci.org/svenkreiss/databench.svg
    :target: https://travis-ci.org/svenkreiss/databench
.. image:: https://coveralls.io/repos/svenkreiss/databench/badge.svg
    :target: https://coveralls.io/r/svenkreiss/databench
.. image:: https://badge.fury.io/py/databench.svg
    :target: https://pypi.python.org/pypi/databench/
.. image:: https://img.shields.io/pypi/dm/databench.svg
    :target: https://pypi.python.org/pypi/databench/


Documentation and License
-------------------------

| `Tutorial, user guide and API documentation <http://databench.trivial.io>`_.
| Databench was written by Sven Kreiss and made available under the `MIT license <https://github.com/svenkreiss/databench/blob/master/LICENSE>`_.


Changelog
---------

* `master <https://github.com/svenkreiss/databench/compare/v0.3.17...master>`_
* `0.3.17 <https://github.com/svenkreiss/databench/compare/v0.3.16...v0.3.17>`_ (2015-05-04)
    * make sure messages to frontend are utf-8 encoded on the python side
* `0.3.16 <https://github.com/svenkreiss/databench/compare/v0.3.15...v0.3.16>`_ (2015-04-27)
    * add auto-reconnect for WebSocket connections (three attempts with exponential and randomized back-off)
    * add full stacktrace to some situations where it was suppressed before (especially for import bugs)
* `0.3.15 <https://github.com/svenkreiss/databench/compare/v0.3.9...v0.3.15>`_ (2015-04-17)
    * introduce optional ``request_args`` parameter to ``Analysis.on_connect()`` function
    * use wss when used over https
    * scaffolding: check analysis names for dashes and warn
    * workaround different JSON specs: convert nan, +inf and -inf to strings
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
