# Databench

> Data analysis tool using Flask, Socket.IO and d3.js. Optional parallelization with Redis Queue and visualizations with mpld3. Live demos are at [databench-examples-viewer.svenkreiss.com](http://databench-examples-viewer.svenkreiss.com).

[![Build Status](https://travis-ci.org/svenkreiss/databench.png?branch=master)](https://travis-ci.org/svenkreiss/databench)


## Documentation

User guide and API documentation: [www.svenkreiss.com/databench/](http://www.svenkreiss.com/databench/)


## License
Databench was written by Sven Kreiss and made available under the [MIT license](https://github.com/svenkreiss/databench/blob/master/LICENSE).


## Development

* 0.3.0:
    * moved from socket.io to plain websockets
    * one analysis instance per websocket connection
    * restructured analyses directories
    * signals are executed in separate co-routines
    * interface to other backends using `zmq`
    * frontend: genericElements take string ids instead of jquery selectors
