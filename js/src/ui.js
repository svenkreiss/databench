
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

    render = () => {
        while(this._messages.length > this.limit) this._messages.shift();
        this.node.innerText = this._messages.map((m) => m.join('')).join('\n');
    };

    add = (message, source='unknown') => {
        if (typeof message != "string") {
            message = JSON.stringify(message);
        }

        let padded_source = ' '.repeat(Math.max(0, 8 - source.length)) + source;
        this._messages.push([`${padded_source}: ${message}`]);
        this.render();
    };

    static wire(id='log', source='backend', limit=20, consoleFnName='log') {
        let node = document.getElementById(id);
        if (node == null) return;

        console.log(`Wiring element id=${id} to ${source}.`);
        let l = new Log(node, limit, consoleFnName);
        return (message) => l.add(message, source);
    }
};


export class StatusLog {
    constructor(node, formatter=StatusLog.default_alert) {
        this.node = node;
        this.formatter = formatter;
        this._messages = new Map();
    }

    static default_alert(msg, c) {
        let c_format = c <= 1 ? '' : `<b>(${c})</b> `;
        return `<div class="alert alert-danger">${c_format}${msg}</div>`;
    }

    render = () => {
        let formatted = [...this._messages].map(([m, c]) => this.formatter(m, c));
        this.node.innerHTML = formatted.join('\n');
    };

    add = (msg) => {
        if (msg == null) {
            this._messages.clear();
            return;
        }
        if (typeof msg != "string") {
            msg = JSON.stringify(msg);
        }

        if (this._messages.has(msg)) {
            this._messages.set(msg, this._messages.get(msg) + 1);
        } else {
            this._messages.set(msg, 1);
        }
        this.render();
    };

    static wire(id='ws-alerts', formatter=StatusLog.default_alert) {
        let node = document.getElementById(id);
        if (node == null) return;

        console.log(`Wiring element id=${id}.`);
        let l = new StatusLog(node, formatter);
        return l.add;
    }
};
