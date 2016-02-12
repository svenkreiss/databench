
export class Connection {
    constructor(error_cb, analysis_id, ws_url) {
        this.error_cb = error_cb;
        this.analysis_id = analysis_id;
        this.ws_url = ws_url ? ws_url : this.guess_ws_url();

        this.on_callbacks = {};
        this.onAction_callbacks = {};

        this.ws_reconnect_attempt = 0;
        this.ws_reconnect_delay = 100.0;

        this.socket = null;
        this.socket_check_open = null;
        this.ws_connect();
    }

    guess_ws_url() {
        let ws_protocol = 'ws';
        if (location.origin.startsWith('https://')) ws_protocol = 'wss';

        let path = location.pathname.substring(0, location.pathname.lastIndexOf('/'));
        return `${ws_protocol}://${document.domain}:${location.port}${path}/ws`;
    }

    ws_connect() {
        this.socket = new WebSocket(this.ws_url);
        console.log('connect');
        console.log(this);
        this.socket_check_open = setInterval(this.ws_check_open, 2000);

        this.socket.onopen = this.ws_onopen;
        this.socket.onclose = this.ws_onclose;
        this.socket.onmessage = this.ws_onmessage;
    }

    ws_check_open() {
        if (this.readyState == WebSocket.CONNECTING) {
            return;
        }
        if (this.readyState != WebSocket.OPEN) {
            this.error_cb(
                'Connection could not be opened. '+
                'Please <a href="javascript:location.reload(true);" '+
                'class="alert-link">reload</a> this page to try again.'
            );
        }
        window.clearInterval(this.socket_check_open);
    }

    ws_onopen() {
        console.log('onopen');
        console.log(this);
        this.ws_reconnect_attempt = 0;
        this.ws_reconnect_delay = 100.0;
        this.error_cb();  // clear errors
        this.send(JSON.stringify({'__connect': this.analysis_id}));
    }

    ws_onclose() {
        window.clearInterval(this.socket_check_open);

        ws_reconnect_attempt += 1;
        ws_reconnect_delay *= 2;

        if (ws_reconnect_attempt > 3) {
            this.error_cb(
                'Connection closed. '+
                'Please <a href="javascript:location.reload(true);" '+
                'class="alert-link">reload</a> this page to reconnect.'
            );
            return;
        }

        let actual_delay = 0.7 * ws_reconnect_delay + 0.3 * Math.random() * ws_reconnect_delay;
        console.log(`WebSocket reconnect attempt ${ws_reconnect_attempt} in ${actual_delay}ms.`);
        setTimeout(this.ws_connect, actual_delay);
    }

    ws_onmessage(event) {
        let message = JSON.parse(event.data);

        // connect response
        if (message.signal == '__connect') {
            this.analysis_id = message.load.analysis_id;
            console.log('Set analysis_id to ' + analysis_id);
        }

        // actions
        if (message.signal == '__action') {
            let id = message.load.id;
            this.onAction_callbacks[id].map((cb) => cb(message.load.status));
        }

        // normal message
        if (message.signal in on_callbacks) {
            this.on_callbacks[message.signal].map((cb) => cb(message.load));
        }
    }


    on(signalName, callback) {
        if (!(signalName in this.on_callbacks))
            this.on_callbacks[signalName] = [];
        this.on_callbacks[signalName].push(callback);
    }

    emit(signalName, message) {
        if (this.socket.readyState != 1) {
            setTimeout(() => emit(signalName, message), 5);
            return;
        }
        this.socket.send(JSON.stringify({'signal':signalName, 'load':message}));
    }

    onAction(actionID, callback) {
        if (!(actionID in this.onAction_callbacks))
            this.onAction_callbacks[actionID] = [];
        this.onAction_callbacks[actionID].push(callback);
    }
}
