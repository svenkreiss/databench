
function Databench(name) {
	var _name = name;

	var socket = io.connect('http://'+document.domain+':'+location.port+'/'+_name);



	var signals = {};

	signals.on = function(signalName, callback) {
		socket.on(signalName, callback);
	};

	signals.emit = function(signalName, message) {
		socket.emit(signalName, message);
	};



	var genericElements = {};

	genericElements.log = function(selector, signal_name, limit, console_fn_name) {
		if (!signal_name) signal_name = 'log';
		if (!limit) limit = 20;
		if (!console_fn_name) console_fn_name = 'log';

		var _messages = [];

		// update
		function update() {
			if (_messages.length > limit) {
				_messages.shift();
			}
			selector.html(_messages.join('<br />'));
		}

		// capture events from frontend
		var _console_fn_original = console[console_fn_name];
	    console[console_fn_name] = function(msg) {
	        _console_fn_original.apply(console, ["frontend:", msg]);
	        _messages.push("frontend: "+msg);

	        update();
	    }

		// listen for _messages from backend
		socket.on(signal_name, function(message) {
			var msg = JSON.stringify(message);

			_console_fn_original.apply(console, [" backend:", msg]);
			_messages.push(" backend: "+msg);

			update();
		});
	};

	genericElements.mpld3canvas = function(selector, signalName) {
		if (!signalName) signalName = 'mpld3canvas';

		socket.on(signalName, function(msg) {
			console.log("removing old figure");
			selector.html('');
			console.log("drawing mpld3 on element "+selector.attr('id'));
			mpld3.draw_figure(selector.attr('id'), msg);
		});
	};




	var publicFunctions = {
		'signals': signals,
		'genericElements': genericElements,
	};

	return publicFunctions;
};
