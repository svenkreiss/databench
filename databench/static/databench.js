
function Databench(name) {
	var _name = name;
	var on_callbacks = {};

	var socket = new WebSocket('ws://'+document.domain+':'+location.port+'/'+_name+'/ws');

	socket.onmessage = function(event) {
		var message_data = JSON.parse(event.data);
		if(!(message_data.signal in on_callbacks)) return;

		for(cb in on_callbacks[message_data.signal]) {
			on_callbacks[message_data.signal][cb](message_data.message);
		}
	}


	var on = function(signalName, callback) {
		if(!(signalName in on_callbacks))
			on_callbacks[signalName] = [];
		on_callbacks[signalName].push(callback);
	};

	var emit = function(signalName, message) {
		if(socket.readyState != 1) {
			setTimeout(function() {
				emit(signalName, message);
			}, 5);
			return;
		}
		socket.send(JSON.stringify({'signal':signalName, 'message':message}));
	};



	var genericElements = {};

	genericElements.log = function(selector, signal_name, limit, console_fn_name) {
		if (!signal_name) signal_name = 'log';
		if (!limit) limit = 20;
		if (!console_fn_name) console_fn_name = 'log';

		var _selector = $('#'+selector);
		var _messages = [];

		// update
		function update() {
			if (_messages.length > limit) {
				_messages.shift();
			}
			if (_selector) _selector.html(_messages.join('<br />'));
		}

		// capture events from frontend
		var _console_fn_original = console[console_fn_name];
	    console[console_fn_name] = function(msg) {
	        _console_fn_original.apply(console, ["frontend:", msg]);
	        _messages.push("frontend: "+msg);

	        update();
	    }

		// listen for _messages from backend
		on(signal_name, function(message) {
			var msg = JSON.stringify(message);

			_console_fn_original.apply(console, [" backend:", msg]);
			_messages.push(" backend: "+msg);

			update();
		});
	};

	genericElements.mpld3canvas = function(selector, signalName) {
		if (!signalName) signalName = 'mpld3canvas';

		var _selector = $('#'+selector);

		on(signalName, function(msg) {
			if (_selector) _selector.html('');
			mpld3.draw_figure(selector, msg);
		});
	};




	var publicFunctions = {
		'on': on, 'emit': emit,
		'genericElements': genericElements,
	};

	return publicFunctions;
};
