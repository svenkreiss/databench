
function Databench(name) {
	var _name = name;

	var socket = io.connect('http://'+document.domain+':'+location.port+'/'+_name);



	var signals = {}

	signals.on = function(signalName, callback) {
		socket.on(signalName, callback);
	};

	signals.emit = function(signalName, message) {
		socket.emit(signalName, message);
	};



	var genericElements = {'log': null}

	socket.on('log', function(msg) {
		if (genericElements.log) {
			genericElements.log.prepend(JSON.stringify(msg)+'<br />');
		}
	});




	var publicFunctions = {
		'signals': signals, 
		'genericElements': genericElements,
	};


	return publicFunctions;
};
