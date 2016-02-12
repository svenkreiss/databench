(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var Connection = exports.Connection = function () {
    function Connection(error_cb, analysis_id, ws_url) {
        _classCallCheck(this, Connection);

        this.error_cb = error_cb;
        this.analysis_id = analysis_id;
        this.ws_url = ws_url ? ws_url : this.guess_ws_url();

        this.on_callbacks = {};
        this.onAction_callbacks = {};

        this.ws_reconnect_attempt = 0;
        this.ws_reconnect_delay = 100.0;

        this.socket = null;
        this.socket_check_open = null;
        this.ws_connect();
    }

    _createClass(Connection, [{
        key: 'guess_ws_url',
        value: function guess_ws_url() {
            var ws_protocol = 'ws';
            if (location.origin.startsWith('https://')) ws_protocol = 'wss';

            var path = location.pathname.substring(0, location.pathname.lastIndexOf('/'));
            return ws_protocol + '://' + document.domain + ':' + location.port + path + '/ws';
        }
    }, {
        key: 'ws_connect',
        value: function ws_connect() {
            this.socket = new WebSocket(this.ws_url);
            console.log('connect');
            console.log(this);
            this.socket_check_open = setInterval(this.ws_check_open, 2000);

            this.socket.onopen = this.ws_onopen;
            this.socket.onclose = this.ws_onclose;
            this.socket.onmessage = this.ws_onmessage;
        }
    }, {
        key: 'ws_check_open',
        value: function ws_check_open() {
            if (this.readyState == WebSocket.CONNECTING) {
                return;
            }
            if (this.readyState != WebSocket.OPEN) {
                this.error_cb('Connection could not be opened. ' + 'Please <a href="javascript:location.reload(true);" ' + 'class="alert-link">reload</a> this page to try again.');
            }
            window.clearInterval(this.socket_check_open);
        }
    }, {
        key: 'ws_onopen',
        value: function ws_onopen() {
            console.log('onopen');
            console.log(this);
            this.ws_reconnect_attempt = 0;
            this.ws_reconnect_delay = 100.0;
            this.error_cb(); // clear errors
            this.send(JSON.stringify({ '__connect': this.analysis_id }));
        }
    }, {
        key: 'ws_onclose',
        value: function ws_onclose() {
            window.clearInterval(this.socket_check_open);

            ws_reconnect_attempt += 1;
            ws_reconnect_delay *= 2;

            if (ws_reconnect_attempt > 3) {
                this.error_cb('Connection closed. ' + 'Please <a href="javascript:location.reload(true);" ' + 'class="alert-link">reload</a> this page to reconnect.');
                return;
            }

            var actual_delay = 0.7 * ws_reconnect_delay + 0.3 * Math.random() * ws_reconnect_delay;
            console.log('WebSocket reconnect attempt ' + ws_reconnect_attempt + ' in ' + actual_delay + 'ms.');
            setTimeout(this.ws_connect, actual_delay);
        }
    }, {
        key: 'ws_onmessage',
        value: function ws_onmessage(event) {
            var message = JSON.parse(event.data);

            // connect response
            if (message.signal == '__connect') {
                this.analysis_id = message.load.analysis_id;
                console.log('Set analysis_id to ' + analysis_id);
            }

            // actions
            if (message.signal == '__action') {
                var id = message.load.id;
                this.onAction_callbacks[id].map(function (cb) {
                    return cb(message.load.status);
                });
            }

            // normal message
            if (message.signal in on_callbacks) {
                this.on_callbacks[message.signal].map(function (cb) {
                    return cb(message.load);
                });
            }
        }
    }, {
        key: 'on',
        value: function on(signalName, callback) {
            if (!(signalName in this.on_callbacks)) this.on_callbacks[signalName] = [];
            this.on_callbacks[signalName].push(callback);
        }
    }, {
        key: 'emit',
        value: function (_emit) {
            function emit(_x, _x2) {
                return _emit.apply(this, arguments);
            }

            emit.toString = function () {
                return _emit.toString();
            };

            return emit;
        }(function (signalName, message) {
            if (this.socket.readyState != 1) {
                setTimeout(function () {
                    return emit(signalName, message);
                }, 5);
                return;
            }
            this.socket.send(JSON.stringify({ 'signal': signalName, 'load': message }));
        })
    }, {
        key: 'onAction',
        value: function onAction(actionID, callback) {
            if (!(actionID in this.onAction_callbacks)) this.onAction_callbacks[actionID] = [];
            this.onAction_callbacks[actionID].push(callback);
        }
    }]);

    return Connection;
}();

},{}],2:[function(require,module,exports){
'use strict';

var _ui = require('./ui');

var ui = _interopRequireWildcard(_ui);

var _connection = require('./connection');

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

// create a public interface
var Databench04 = window.Databench04 || {};
Databench04.ui = ui;
Databench04.Connection = _connection.Connection;
window.Databench04 = Databench04;

},{"./connection":1,"./ui":3}],3:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
	value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var Log = exports.Log = function () {
	function Log(node) {
		var _this = this;

		var limit = arguments.length <= 1 || arguments[1] === undefined ? 20 : arguments[1];
		var consoleFnName = arguments.length <= 2 || arguments[2] === undefined ? 'log' : arguments[2];

		_classCallCheck(this, Log);

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

	_createClass(Log, [{
		key: 'render',
		value: function render() {
			while (this._messages.length > this.limit) {
				this._messages.shift();
			} // for HTML output, json-stringify messages and join with <br>
			this.node.innerText = this._messages.map(function (m) {
				return m.join('');
			}).join('\n');
		}
	}, {
		key: 'add',
		value: function add(message) {
			var source = arguments.length <= 1 || arguments[1] === undefined ? 'unknown' : arguments[1];

			if (typeof message != "string") {
				message = JSON.stringify(message);
			}

			this._messages.push([' '.repeat(Math.max(0, 8 - source.length)) + source + ': ', message]);
			this.render();
		}
	}], [{
		key: 'wire',
		value: function wire() {
			var id = arguments.length <= 0 || arguments[0] === undefined ? 'log' : arguments[0];
			var source = arguments.length <= 1 || arguments[1] === undefined ? 'backend' : arguments[1];
			var limit = arguments.length <= 2 || arguments[2] === undefined ? 20 : arguments[2];
			var consoleFnName = arguments.length <= 3 || arguments[3] === undefined ? 'log' : arguments[3];

			var node = document.getElementById(id);
			if (node == null) return;

			console.log('Wiring element id=' + id + ' to ' + source + '.');
			var l = new Log(node, limit, consoleFnName);
			return function (message) {
				l.add(message, source);
			};
		}
	}]);

	return Log;
}();

;

},{}]},{},[2])


//# sourceMappingURL=databench_04.js.map
