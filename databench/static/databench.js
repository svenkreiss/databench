
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

	genericElements.log = function(selector, limit) {
		if (!limit) limit = 20;

		var _selector = selector;
		var _limit = limit;

		var messages = [];

		socket.on('log', function(msg) {
			messages.push(JSON.stringify(msg));
			if (messages.length > _limit) {
				messages.shift();
			}
			_selector.html(messages.join('<br />'));
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
