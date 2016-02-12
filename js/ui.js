
export class Log {
	constructor(node, limit=20, consoleFnName='log') {
		this.node = node;
		this.limit = limit;
		this.consoleFnName = consoleFnName;

		this._messages = [];

		// capture events from frontend
		let _consoleFnOriginal = console[consoleFnName];
		console[consoleFnName] = (message) => {
			this.add(message, 'frontend');
			_consoleFnOriginal.apply(console, [message]);
		}
	}

	render() {
		while(this._messages.length > this.limit) this._messages.shift();

		// for HTML output, json-stringify messages and join with <br>
		this.node.innerText = this._messages.map((m) => m.join('')).join('\n');
	}

	add(message, source='unknown') {
		if (typeof message != "string") {
			message = JSON.stringify(message);
		}

		this._messages.push([' '.repeat(Math.max(0, 8 - source.length)) + source + ': ', message]);
		this.render();
	};

	static wire(id='log', source='backend', limit=20, consoleFnName='log') {
		let node = document.getElementById(id);
		if (node == null) return;

		console.log(`Wiring element id=${id} to ${source}.`);
		let l = new Log(node, limit, consoleFnName);
		return function(message) { l.add(message, source); };
	}
};
