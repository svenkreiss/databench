if (typeof WebSocket === 'undefined') {
    var WebSocket = require('websocket').w3cwebsocket;
}

export class Connection {
    constructor(analysis_id=null, ws_url=null) {
        this.analysis_id = analysis_id;
        this.ws_url = ws_url ? ws_url : Connection.guess_ws_url();

        this.error_cb = null;
        this.on_callbacks = {};
        this.onAction_callbacks = {};

        this.ws_reconnect_attempt = 0;
        this.ws_reconnect_delay = 100.0;

        this.socket = null;
        this.socket_check_open = null;
    }

    static guess_ws_url() {
        var ws_protocol = 'ws';
        if (location.origin.startsWith('https://')) ws_protocol = 'wss';

        let path = location.pathname.substring(0, location.pathname.lastIndexOf('/'));
        return `${ws_protocol}://${document.domain}:${location.port}${path}/ws`;
    };

    connect = () => {
        this.socket = new WebSocket(this.ws_url);

        this.socket_check_open = setInterval(this.ws_check_open, 2000);
        this.socket.onopen = this.ws_onopen;
        this.socket.onclose = this.ws_onclose;
        this.socket.onmessage = this.ws_onmessage;
        return this;
    };

    ws_check_open = () => {
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
    };

    ws_onopen = () => {
        this.ws_reconnect_attempt = 0;
        this.ws_reconnect_delay = 100.0;
        this.error_cb();  // clear errors
        this.socket.send(JSON.stringify({'__connect': this.analysis_id}));
    };

    ws_onclose = () => {
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
        console.log(`WebSocket reconnect attempt ${this.ws_reconnect_attempt} in ${actual_delay}ms.`);
        setTimeout(this.connect, actual_delay);
    };

    ws_onmessage = (event) => {
        let message = JSON.parse(event.data);

        // connect response
        if (message.signal == '__connect') {
            this.analysis_id = message.load.analysis_id;
            console.log('Set analysis_id to ' + this.analysis_id);
        }

        // actions
        if (message.signal == '__action') {
            let id = message.load.id;
            this.onAction_callbacks[id].map((cb) => cb(message.load.status));
        }

        // normal message
        if (message.signal in this.on_callbacks) {
            this.on_callbacks[message.signal].map((cb) => cb(message.load));
        }
    };


    on = (signalName, callback) => {
        if (!(signalName in this.on_callbacks))
            this.on_callbacks[signalName] = [];
        this.on_callbacks[signalName].push(callback);
        return this;
    };

    emit = (signalName, message) => {
        if (this.socket.readyState != 1) {
            setTimeout(() => this.emit(signalName, message), 5);
            return;
        }
        this.socket.send(JSON.stringify({'signal':signalName, 'load':message}));
        return this;
    };

    onAction = (actionID, callback) => {
        if (!(actionID in this.onAction_callbacks))
            this.onAction_callbacks[actionID] = [];
        this.onAction_callbacks[actionID].push(callback);
        return this;
    };
}
