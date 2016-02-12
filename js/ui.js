
export class Log {
	constructor(node, limit=20, consoleFnName='log') {
		this.node = node;
		this.limit = limit;
		this.consoleFnName = consoleFnName;

		this._messages = [];

		// capture events from frontend
		this._consoleFnOriginal = console[consoleFnName];
		console[consoleFnName] = (msg) => this.add(msg, 'frontend:');
	}

	render() {
		while(this._messages.length > this.limit) this._messages.shift();

		// for HTML output, json-stringify messages and join with <br>
		this.node.innerText = this._messages.map((m) => m.join('')).join('\n');
	}

	add(message, source='unknown:') {
		this._consoleFnOriginal.apply(console, [message]);
		this._messages.push([source, message]);
		this.render();
	};
};
