if (typeof WebSocket === 'undefined') {
    var WebSocket = require('websocket').w3cwebsocket;
}

export class Connection {
    constructor(analysis_id=null, ws_url=null) {
        this.analysis_id = analysis_id;
        this.ws_url = ws_url ? ws_url : Connection.guess_ws_url();

        this.error_cb = (msg) => {
            if (msg != null)
                return console.log(`connection error: ${msg}`);
        }
        this.on_callbacks = [];
        this._on_callbacks_optimized = null;
        this.onProcess_callbacks = {};

        this.ws_reconnect_attempt = 0;
        this.ws_reconnect_delay = 100.0;

        this.socket = null;
        this.socket_check_open = null;

        // bind methods
        this.connect = this.connect.bind(this);
        this.ws_check_open = this.ws_check_open.bind(this);
        this.ws_onopen = this.ws_onopen.bind(this);
        this.ws_onclose = this.ws_onclose.bind(this);
        this.ws_onmessage = this.ws_onmessage.bind(this);
        this.optimize_on_callbacks = this.optimize_on_callbacks.bind(this);
        this.on = this.on.bind(this);
        this.emit = this.emit.bind(this);
        this.onProcess = this.onProcess.bind(this);
    }

    static guess_ws_url() {
        var ws_protocol = 'ws';
        if (location.origin.startsWith('https://')) ws_protocol = 'wss';

        let path = location.pathname.substring(0, location.pathname.lastIndexOf('/'));
        return `${ws_protocol}://${document.domain}:${location.port}${path}/ws`;
    }

    connect() {
        this.socket = new WebSocket(this.ws_url);

        this.socket_check_open = setInterval(this.ws_check_open, 2000);
        this.socket.onopen = this.ws_onopen;
        this.socket.onclose = this.ws_onclose;
        this.socket.onmessage = this.ws_onmessage;
        return this;
    }

    ws_check_open() {
        if (this.socket.readyState == this.socket.CONNECTING) {
            return;
        }
        if (this.socket.readyState != this.socket.OPEN) {
            this.error_cb(
                'Connection could not be opened. '+
                'Please <a href="javascript:location.reload(true);" '+
                'class="alert-link">reload</a> this page to try again.'
            );
        }
        clearInterval(this.socket_check_open);
    }

    ws_onopen() {
        this.ws_reconnect_attempt = 0;
        this.ws_reconnect_delay = 100.0;
        this.error_cb();  // clear errors
        this.socket.send(JSON.stringify({'__connect': this.analysis_id}));
    }

    ws_onclose() {
        clearInterval(this.socket_check_open);

        this.ws_reconnect_attempt += 1;
        this.ws_reconnect_delay *= 2;

        if (this.ws_reconnect_attempt > 3) {
            this.error_cb(
                'Connection closed. '+
                'Please <a href="javascript:location.reload(true);" '+
                'class="alert-link">reload</a> this page to reconnect.'
            );
            return;
        }

        let actual_delay = 0.7 * this.ws_reconnect_delay + 0.3 * Math.random() * this.ws_reconnect_delay;
        console.log(`WebSocket reconnect attempt ${this.ws_reconnect_attempt} in ${actual_delay.toFixed(0)}ms.`);
        setTimeout(this.connect, actual_delay);
    }

    ws_onmessage(event) {
        let message = JSON.parse(event.data);

        // connect response
        if (message.signal == '__connect') {
            this.analysis_id = message.load.analysis_id;
        }

        // processes
        if (message.signal == '__process') {
            let id = message.load.id;
            let status = message.load.status;
            this.onProcess_callbacks[id].map(cb => cb(status));
        }

        // normal message
        if (this._on_callbacks_optimized === null)
            this.optimize_on_callbacks();
        if (message.signal in this._on_callbacks_optimized) {
            this._on_callbacks_optimized[message.signal].map(
                cb => cb(message.load)
            );
        }
    }

    optimize_on_callbacks() {
        this._on_callbacks_optimized = {};
        this.on_callbacks.map(({signal, callback}) => {
            if (typeof signal === "string") {
                if (!(signal in this._on_callbacks_optimized))
                    this._on_callbacks_optimized[signal] = [];
                this._on_callbacks_optimized[signal].push(callback);
            }else if(typeof signal === "object") {
                for (let signalName in signal) {
                    let entryName = signal[signalName];
                    let filtered_callback = data => {
                        if (data.hasOwnProperty(entryName)) {
                            callback(data[entryName]);
                        }
                    };

                    if (!(signalName in this._on_callbacks_optimized))
                        this._on_callbacks_optimized[signalName] = [];

                    // only use the filtered callback if the entry was not empty
                    if (entryName) {
                        this._on_callbacks_optimized[signalName].push(filtered_callback);
                    } else {
                        this._on_callbacks_optimized[signalName].push(callback);
                    }
                }
            }
        });
    }

    on(signal, callback) {
        this.on_callbacks.push({signal, callback});
        this._on_callbacks_optimized = null;
        return this;
    }

    emit(signalName, message) {
        if (this.socket == null  ||  this.socket.readyState != this.socket.OPEN) {
            setTimeout(() => this.emit(signalName, message), 5);
            return;
        }
        this.socket.send(JSON.stringify({'signal':signalName, 'load':message}));
        return this;
    }

    onProcess(processID, callback) {
        if (!(processID in this.onProcess_callbacks))
            this.onProcess_callbacks[processID] = [];
        this.onProcess_callbacks[processID].push(callback);
        return this;
    }
}
