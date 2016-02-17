(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

if (typeof WebSocket === 'undefined') {
    var WebSocket = require('websocket').w3cwebsocket;
}

var Connection = exports.Connection = function () {
    function Connection() {
        var _this = this;

        var analysis_id = arguments.length <= 0 || arguments[0] === undefined ? null : arguments[0];
        var ws_url = arguments.length <= 1 || arguments[1] === undefined ? null : arguments[1];

        _classCallCheck(this, Connection);

        this.connect = function () {
            _this.socket = new WebSocket(_this.ws_url);

            _this.socket_check_open = setInterval(_this.ws_check_open, 2000);
            _this.socket.onopen = _this.ws_onopen;
            _this.socket.onclose = _this.ws_onclose;
            _this.socket.onmessage = _this.ws_onmessage;
            return _this;
        };

        this.ws_check_open = function () {
            if (_this.socket.readyState == _this.socket.CONNECTING) {
                return;
            }
            if (_this.socket.readyState != _this.socket.OPEN) {
                _this.error_cb('Connection could not be opened. ' + 'Please <a href="javascript:location.reload(true);" ' + 'class="alert-link">reload</a> this page to try again.');
            }
            clearInterval(_this.socket_check_open);
        };

        this.ws_onopen = function () {
            _this.ws_reconnect_attempt = 0;
            _this.ws_reconnect_delay = 100.0;
            _this.error_cb(); // clear errors
            _this.socket.send(JSON.stringify({ '__connect': _this.analysis_id }));
        };

        this.ws_onclose = function () {
            clearInterval(_this.socket_check_open);

            _this.ws_reconnect_attempt += 1;
            _this.ws_reconnect_delay *= 2;

            if (_this.ws_reconnect_attempt > 3) {
                _this.error_cb('Connection closed. ' + 'Please <a href="javascript:location.reload(true);" ' + 'class="alert-link">reload</a> this page to reconnect.');
                return;
            }

            var actual_delay = 0.7 * _this.ws_reconnect_delay + 0.3 * Math.random() * _this.ws_reconnect_delay;
            console.log('WebSocket reconnect attempt ' + _this.ws_reconnect_attempt + ' in ' + actual_delay + 'ms.');
            setTimeout(_this.connect, actual_delay);
        };

        this.ws_onmessage = function (event) {
            var message = JSON.parse(event.data);

            // connect response
            if (message.signal == '__connect') {
                _this.analysis_id = message.load.analysis_id;
                console.log('Set analysis_id to ' + _this.analysis_id);
            }

            // actions
            if (message.signal == '__action') {
                var id = message.load.id;
                _this.onAction_callbacks[id].map(function (cb) {
                    return cb(message.load.status);
                });
            }

            // normal message
            if (message.signal in _this.on_callbacks) {
                _this.on_callbacks[message.signal].map(function (cb) {
                    return cb(message.load);
                });
            }
        };

        this.on = function (signalName, callback) {
            if (!(signalName in _this.on_callbacks)) _this.on_callbacks[signalName] = [];
            _this.on_callbacks[signalName].push(callback);
            return _this;
        };

        this.emit = function (signalName, message) {
            if (_this.socket.readyState != 1) {
                setTimeout(function () {
                    return _this.emit(signalName, message);
                }, 5);
                return;
            }
            _this.socket.send(JSON.stringify({ 'signal': signalName, 'load': message }));
            return _this;
        };

        this.onAction = function (actionID, callback) {
            if (!(actionID in _this.onAction_callbacks)) _this.onAction_callbacks[actionID] = [];
            _this.onAction_callbacks[actionID].push(callback);
            return _this;
        };

        this.analysis_id = analysis_id;
        this.ws_url = ws_url ? ws_url : Connection.guess_ws_url();

        this.error_cb = null;
        this.on_callbacks = {};
        this.onAction_callbacks = {};

        this.ws_reconnect_attempt = 0;
        this.ws_reconnect_delay = 100.0;

        this.socket = null;
        this.socket_check_open = null;
    }

    _createClass(Connection, null, [{
        key: 'guess_ws_url',
        value: function guess_ws_url() {
            var ws_protocol = 'ws';
            if (location.origin.startsWith('https://')) ws_protocol = 'wss';

            var path = location.pathname.substring(0, location.pathname.lastIndexOf('/'));
            return ws_protocol + '://' + document.domain + ':' + location.port + path + '/ws';
        }
    }]);

    return Connection;
}();

},{"websocket":4}],2:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
	value: true
});
exports.Connection = exports.ui = undefined;

var _ui = require('./ui');

var ui = _interopRequireWildcard(_ui);

var _connection = require('./connection');

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

// create a public interface
if (typeof window !== 'undefined') {
	window.Databench04 = { ui: ui, Connection: _connection.Connection };
}
exports.ui = ui;
exports.Connection = _connection.Connection;

},{"./connection":1,"./ui":3}],3:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _toConsumableArray(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } else { return Array.from(arr); } }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var Log = exports.Log = function () {
    function Log(node) {
        var _this = this;

        var limit = arguments.length <= 1 || arguments[1] === undefined ? 20 : arguments[1];
        var consoleFnName = arguments.length <= 2 || arguments[2] === undefined ? 'log' : arguments[2];

        _classCallCheck(this, Log);

        this.render = function () {
            while (_this._messages.length > _this.limit) {
                _this._messages.shift();
            }_this.node.innerText = _this._messages.map(function (m) {
                return m.join('');
            }).join('\n');
            return _this;
        };

        this.add = function (message) {
            var source = arguments.length <= 1 || arguments[1] === undefined ? 'unknown' : arguments[1];

            if (typeof message != "string") {
                message = JSON.stringify(message);
            }

            var padded_source = ' '.repeat(Math.max(0, 8 - source.length)) + source;
            _this._messages.push([padded_source + ': ' + message]);
            _this.render();
            return _this;
        };

        this.node = node;
        this.limit = limit;
        this.consoleFnName = consoleFnName;
        this._messages = [];

        // capture events from frontend
        var _consoleFnOriginal = console[consoleFnName];
        console[consoleFnName] = function (message) {
            _this.add(message, 'frontend');
            _consoleFnOriginal.apply(console, [message]);
        };
    }

    _createClass(Log, null, [{
        key: 'wire',
        value: function wire(conn) {
            var id = arguments.length <= 1 || arguments[1] === undefined ? 'log' : arguments[1];
            var source = arguments.length <= 2 || arguments[2] === undefined ? 'backend' : arguments[2];
            var limit = arguments.length <= 3 || arguments[3] === undefined ? 20 : arguments[3];
            var consoleFnName = arguments.length <= 4 || arguments[4] === undefined ? 'log' : arguments[4];

            var node = document.getElementById(id);
            if (node == null) return;

            console.log('Wiring element id=' + id + ' to ' + source + '.');
            var l = new Log(node, limit, consoleFnName);
            conn.on('log', function (message) {
                return l.add(message, source);
            });
            return this;
        }
    }]);

    return Log;
}();

;

var StatusLog = exports.StatusLog = function () {
    function StatusLog(node) {
        var _this2 = this;

        var formatter = arguments.length <= 1 || arguments[1] === undefined ? StatusLog.default_alert : arguments[1];

        _classCallCheck(this, StatusLog);

        this.render = function () {
            var formatted = [].concat(_toConsumableArray(_this2._messages)).map(function (_ref) {
                var _ref2 = _slicedToArray(_ref, 2);

                var m = _ref2[0];
                var c = _ref2[1];
                return _this2.formatter(m, c);
            });
            _this2.node.innerHTML = formatted.join('\n');
            return _this2;
        };

        this.add = function (msg) {
            if (msg == null) {
                _this2._messages.clear();
                return;
            }
            if (typeof msg != "string") {
                msg = JSON.stringify(msg);
            }

            if (_this2._messages.has(msg)) {
                _this2._messages.set(msg, _this2._messages.get(msg) + 1);
            } else {
                _this2._messages.set(msg, 1);
            }
            _this2.render();
            return _this2;
        };

        this.node = node;
        this.formatter = formatter;
        this._messages = new Map();
    }

    _createClass(StatusLog, null, [{
        key: 'default_alert',
        value: function default_alert(msg, c) {
            var c_format = c <= 1 ? '' : '<b>(' + c + ')</b> ';
            return '<div class="alert alert-danger">' + c_format + msg + '</div>';
        }
    }, {
        key: 'wire',
        value: function wire(conn) {
            var id = arguments.length <= 1 || arguments[1] === undefined ? 'ws-alerts' : arguments[1];
            var formatter = arguments.length <= 2 || arguments[2] === undefined ? StatusLog.default_alert : arguments[2];

            var node = document.getElementById(id);
            if (node == null) return;

            console.log('Wiring element id=' + id + '.');
            var l = new StatusLog(node, formatter);
            conn.error_cb = l.add;
        }
    }]);

    return StatusLog;
}();

;

},{}],4:[function(require,module,exports){
var _global = (function() { return this; })();
var nativeWebSocket = _global.WebSocket || _global.MozWebSocket;
var websocket_version = require('./version');


/**
 * Expose a W3C WebSocket class with just one or two arguments.
 */
function W3CWebSocket(uri, protocols) {
	var native_instance;

	if (protocols) {
		native_instance = new nativeWebSocket(uri, protocols);
	}
	else {
		native_instance = new nativeWebSocket(uri);
	}

	/**
	 * 'native_instance' is an instance of nativeWebSocket (the browser's WebSocket
	 * class). Since it is an Object it will be returned as it is when creating an
	 * instance of W3CWebSocket via 'new W3CWebSocket()'.
	 *
	 * ECMAScript 5: http://bclary.com/2004/11/07/#a-13.2.2
	 */
	return native_instance;
}


/**
 * Module exports.
 */
module.exports = {
    'w3cwebsocket' : nativeWebSocket ? W3CWebSocket : null,
    'version'      : websocket_version
};

},{"./version":5}],5:[function(require,module,exports){
module.exports = require('../package.json').version;

},{"../package.json":6}],6:[function(require,module,exports){
module.exports={
  "_args": [
    [
      "websocket@^1.0.22",
      "/Users/sven/tech/databench"
    ]
  ],
  "_from": "websocket@>=1.0.22 <2.0.0",
  "_id": "websocket@1.0.22",
  "_inCache": true,
  "_installable": true,
  "_location": "/websocket",
  "_nodeVersion": "3.3.1",
  "_npmUser": {
    "email": "brian@worlize.com",
    "name": "theturtle32"
  },
  "_npmVersion": "2.14.3",
  "_phantomChildren": {},
  "_requested": {
    "name": "websocket",
    "raw": "websocket@^1.0.22",
    "rawSpec": "^1.0.22",
    "scope": null,
    "spec": ">=1.0.22 <2.0.0",
    "type": "range"
  },
  "_requiredBy": [
    "/"
  ],
  "_resolved": "https://registry.npmjs.org/websocket/-/websocket-1.0.22.tgz",
  "_shasum": "8c33e3449f879aaf518297c9744cebf812b9e3d8",
  "_shrinkwrap": null,
  "_spec": "websocket@^1.0.22",
  "_where": "/Users/sven/tech/databench",
  "author": {
    "email": "brian@worlize.com",
    "name": "Brian McKelvey",
    "url": "https://www.worlize.com/"
  },
  "browser": "lib/browser.js",
  "bugs": {
    "url": "https://github.com/theturtle32/WebSocket-Node/issues"
  },
  "config": {
    "verbose": false
  },
  "contributors": [
    {
      "name": "Iñaki Baz Castillo",
      "email": "ibc@aliax.net",
      "url": "http://dev.sipdoc.net"
    }
  ],
  "dependencies": {
    "debug": "~2.2.0",
    "nan": "~2.0.5",
    "typedarray-to-buffer": "~3.0.3",
    "yaeti": "~0.0.4"
  },
  "description": "Websocket Client & Server Library implementing the WebSocket protocol as specified in RFC 6455.",
  "devDependencies": {
    "buffer-equal": "^0.0.1",
    "faucet": "^0.0.1",
    "gulp": "git+https://github.com/gulpjs/gulp.git#4.0",
    "gulp-jshint": "^1.11.2",
    "jshint-stylish": "^1.0.2",
    "tape": "^4.0.1"
  },
  "directories": {
    "lib": "./lib"
  },
  "dist": {
    "shasum": "8c33e3449f879aaf518297c9744cebf812b9e3d8",
    "tarball": "http://registry.npmjs.org/websocket/-/websocket-1.0.22.tgz"
  },
  "engines": {
    "node": ">=0.8.0"
  },
  "gitHead": "19108bbfd7d94a5cd02dbff3495eafee9e901ca4",
  "homepage": "https://github.com/theturtle32/WebSocket-Node",
  "keywords": [
    "RFC-6455",
    "client",
    "comet",
    "networking",
    "push",
    "realtime",
    "server",
    "socket",
    "websocket",
    "websockets"
  ],
  "license": "Apache-2.0",
  "main": "index",
  "maintainers": [
    {
      "name": "theturtle32",
      "email": "brian@worlize.com"
    }
  ],
  "name": "websocket",
  "optionalDependencies": {},
  "readme": "ERROR: No README data found!",
  "repository": {
    "type": "git",
    "url": "git+https://github.com/theturtle32/WebSocket-Node.git"
  },
  "scripts": {
    "gulp": "gulp",
    "install": "(node-gyp rebuild 2> builderror.log) || (exit 0)",
    "test": "faucet test/unit"
  },
  "version": "1.0.22"
}

},{}]},{},[2])


//# sourceMappingURL=databench_04.js.map
