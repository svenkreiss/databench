(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

var _ui = require('./ui');

var ui = _interopRequireWildcard(_ui);

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

// create a public interface
var Databench04 = window.Databench04 || {};
Databench04.ui = ui;
window.Databench04 = Databench04;

},{"./ui":2}],2:[function(require,module,exports){
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

},{}]},{},[1])


//# sourceMappingURL=databench_04.js.map
