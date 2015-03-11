
function Databench(opts) {
	var ws_protocol = 'ws';
	if (location.origin.indexOf("https://") !== -1) ws_protocol = 'wss';
	opts = $.extend({
		ws_url:
			ws_protocol+'://'+document.domain+':'+
			location.port+
			location.pathname.substring(
				0,
				location.pathname.lastIndexOf("/")
			)+
			'/ws',
		content_class_name: 'content',
	}, opts);

	var on_callbacks = {};
	var onAction_callbacks = {};

	var socket = new WebSocket(opts.ws_url);

	// handle problems with websocket connection
	var check_open = setInterval(function() {
		if (socket.readyState == WebSocket.CONNECTING) {
			return;
		}
		if (socket.readyState != WebSocket.OPEN) {
			$('<div class="alert alert-danger">Connection could not be opened. '+
			  'Please <a href="javascript:location.reload(true);" '+
			  'class="alert-link">reload</a> this page to try again.</div>'
			).insertBefore('.'+opts.content_class_name);
		}
		window.clearInterval(check_open);
	}, 2000);
	socket.onclose = function () {
		$('<div class="alert alert-danger">Connection closed. '+
		  'Please <a href="javascript:location.reload(true);" '+
		  'class="alert-link">reload</a> this page to reconnect.</div>'
		).insertBefore('.'+opts.content_class_name);
	}

	// process incoming websocket messages
	socket.onmessage = function(event) {
		var message_data = JSON.parse(event.data);

		// normal message
		if (message_data.signal in on_callbacks) {
			for(cb in on_callbacks[message_data.signal]) {
				on_callbacks[message_data.signal][cb](message_data.load);
			}
		}

		if (message_data.signal == '__action') {
			var id = message_data.load.id
			for(cb in onAction_callbacks[id]) {
				onAction_callbacks[id][cb](message_data.load.status);
			}
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
		socket.send(JSON.stringify({'signal':signalName, 'load':message}));
	};

	var onAction = function(actionID, callback) {
		if (!(actionID in onAction_callbacks))
			onAction_callbacks[actionID] = [];
		onAction_callbacks[actionID].push(callback);
	}



	var genericElements = {};

	genericElements.log = function(id, signalName, limit, consoleFnName) {
		if (!signalName) signalName = 'log';
		if (!limit) limit = 20;
		if (!consoleFnName) consoleFnName = 'log';

		var _selector = null;
		if (id) _selector = $('#'+id);
		var _messages = [];

		// update
		function update() {
			while(_messages.length > limit) {
				_messages.shift();
			}
			if (_selector) {
				// for HTML output, json-stringify messages and join with <br>
				_selector.text(_messages.map(function(m) {
					return m[0] + m[1];
				}).join('\n'));
			}
		}

		// capture events from frontend
		var _consoleFnOriginal = console[consoleFnName];
		console[consoleFnName] = function(msg) {
			_consoleFnOriginal.apply(console, ["frontend:", msg]);
			_messages.push(["frontend:", msg]);

			update();
		}

		// listen for _messages from backend
		on(signalName, function(message) {
			var msg = JSON.stringify(message);

			_consoleFnOriginal.apply(console, [" backend:", msg]);
			_messages.push([" backend:", msg]);

			update();
		});
	};

	genericElements.mpld3canvas = function(id, signalName) {
		if (!signalName) signalName = 'mpld3canvas';

		var _selector = $('#'+id);

		on(signalName, function(msg) {
			if (_selector) _selector.html('');
			mpld3.draw_figure(id, msg);
		});
	};

	genericElements.button = function(selector, signalName) {
		var _selector = selector;
		if ($.type(_selector) == 'string')
			_selector = $('#'+selector);
		if (!signalName)
			signalName = _selector.attr('data-signal-name');
		if (!signalName)
			signalName = selector;

		var state = 'idle';

		_selector.on('click', function() {
			if (state == 'idle') {
				var actionID = Math.floor(Math.random() * 0x100000);
				onAction(actionID, function(status) {
					if (status=='start') {
						_selector.addClass('active');
						state = 'running';
					} else if (status=='end') {
						_selector.removeClass('active');
						state = 'idle';
					}
				});

				// prepare message
				var message = {};
				if (_selector.attr('data-message'))
					message = JSON.parse(_selector.attr('data-message'));
				message['__action_id'] = actionID;

				// send
				emit(signalName, message);
			}
		});
	}

	genericElements.slider = function(selector, signalName) {
		var _selector = selector;
		if ($.type(_selector) == 'string')
			_selector = $('#'+selector);
		if (!signalName)
			signalName = _selector.attr('data-signal-name');
		if (!signalName)
			signalName = _selector.attr('name');
		if (!signalName)
			signalName = selector;

		var _label = $('label[for='+_selector.attr('name')+']')
		var label = _label.html();
		var addedValue = false;

		_selector.on('input change', function() {
			if (label) {
				if (!addedValue) {
					_label.html(label+' ('+this.value+')');
					addedValue = true;
				}else{
					_label.html(label+' ('+this.value+')');
				}
			}
			emit(signalName, [parseFloat(this.value)]);
		});
		_selector.trigger('input');
	}


	// initialize genericElements from ids found on the page
	// mpld3canvas
	$("div[id^='mpld3canvas']").each(function() {
		var name = $(this).attr('id');
		console.log('Initialize databench.genericElements.mpld3canvas(id='+name+').');
		genericElements.mpld3canvas(name);
	});
	// button
	$("button[data-signal-name]").each(function() {
		var name = $(this).attr('data-signal-name');
		console.log('Initialize databench.genericElements.button() with signalName='+name+'.');
		genericElements.button($(this));
	});
	// sliders (input[range])
	$("input[type='range']").each(function() {
		var name = $(this).attr('name');
		console.log('Initialize databench.genericElements.slider() with signalName='+name+'.');
		genericElements.slider($(this));
	});
	// log
	$("pre[id^='log']").each(function() {
		var name = $(this).attr('id');
		console.log('Initialize databench.genericElements.log(id='+name+').');
		genericElements.log(name);
	});


	var publicFunctions = {
		'on': on, 'emit': emit,
		'genericElements': genericElements,
	};

	return publicFunctions;
};
