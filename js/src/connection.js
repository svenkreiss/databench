if (typeof WebSocket === 'undefined') {  // eslint-disable-line
  var WebSocket = require('websocket').w3cwebsocket;  // eslint-disable-line
}

export class Connection {
  constructor(analysis_id = null, ws_url = null, request_args = null) {
    this.analysis_id = analysis_id;
    this.ws_url = ws_url || Connection.guess_ws_url();
    this.request_args = (request_args == null && (typeof window !== 'undefined')) ?
                        window.location.search : request_args;

    this.error_cb = msg => (msg != null ? console.log(`connection error: ${msg}`) : null);
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
    let ws_protocol = 'ws';
    if (location.origin.startsWith('https://')) ws_protocol = 'wss';

    const path = location.pathname.substring(0, location.pathname.lastIndexOf('/'));
    return `${ws_protocol}://${document.domain}:${location.port}${path}/ws`;
  }

  connect() {
    this.socket = new WebSocket(this.ws_url);  // eslint-disable-line

    this.socket_check_open = setInterval(this.ws_check_open, 2000);
    this.socket.onopen = this.ws_onopen;
    this.socket.onclose = this.ws_onclose;
    this.socket.onmessage = this.ws_onmessage;
    return this;
  }

  ws_check_open() {
    if (this.socket.readyState === this.socket.CONNECTING) {
      return;
    }
    if (this.socket.readyState !== this.socket.OPEN) {
      this.error_cb(
        'Connection could not be opened. ' +
        'Please <a href="javascript:location.reload(true);" ' +
        'class="alert-link">reload</a> this page to try again.'
      );
    }
    clearInterval(this.socket_check_open);
  }

  ws_onopen() {
    this.ws_reconnect_attempt = 0;
    this.ws_reconnect_delay = 100.0;
    this.error_cb();  // clear errors
    this.socket.send(JSON.stringify({
      __connect: this.analysis_id,
      __request_args: this.request_args,
    }));
  }

  ws_onclose() {
    clearInterval(this.socket_check_open);

    this.ws_reconnect_attempt += 1;
    this.ws_reconnect_delay *= 2;

    if (this.ws_reconnect_attempt > 3) {
      this.error_cb(
        'Connection closed. ' +
        'Please <a href="javascript:location.reload(true);" ' +
        'class="alert-link">reload</a> this page to reconnect.'
      );
      return;
    }

    const actual_delay = 0.7 * this.ws_reconnect_delay + 0.3 * Math.random() *
                         this.ws_reconnect_delay;
    console.log(`WebSocket reconnect attempt ${this.ws_reconnect_attempt} ` +
                `in ${actual_delay.toFixed(0)}ms.`);
    setTimeout(this.connect, actual_delay);
  }

  ws_onmessage(event) {
    const message = JSON.parse(event.data);

    // connect response
    if (message.signal === '__connect') {
      this.analysis_id = message.load.analysis_id;
    }

    // processes
    if (message.signal === '__process') {
      const id = message.load.id;
      const status = message.load.status;
      this.onProcess_callbacks[id].map(cb => cb(status));
    }

    // normal message
    if (this._on_callbacks_optimized === null) this.optimize_on_callbacks();
    if (message.signal in this._on_callbacks_optimized) {
      this._on_callbacks_optimized[message.signal].map(cb => cb(message.load));
    }
  }

  optimize_on_callbacks() {
    this._on_callbacks_optimized = {};
    this.on_callbacks.forEach(({ signal, callback }) => {
      if (typeof signal === 'string') {
        if (!(signal in this._on_callbacks_optimized)) {
          this._on_callbacks_optimized[signal] = [];
        }
        this._on_callbacks_optimized[signal].push(callback);
      } else if (typeof signal === 'object') {
        Object.keys(signal).forEach(signalName => {
          const entryName = signal[signalName];
          const filtered_callback = data => {
            if (data.hasOwnProperty(entryName)) {
              callback(data[entryName]);
            }
          };

          if (!(signalName in this._on_callbacks_optimized)) {
            this._on_callbacks_optimized[signalName] = [];
          }

          // only use the filtered callback if the entry was not empty
          if (entryName) {
            this._on_callbacks_optimized[signalName].push(filtered_callback);
          } else {
            this._on_callbacks_optimized[signalName].push(callback);
          }
        });
      }
    });
  }

  on(signal, callback) {
    this.on_callbacks.push({ signal, callback });
    this._on_callbacks_optimized = null;
    return this;
  }

  emit(signalName, message) {
    if (this.socket == null || this.socket.readyState !== this.socket.OPEN) {
      setTimeout(() => this.emit(signalName, message), 5);
      return this;
    }
    this.socket.send(JSON.stringify({ signal: signalName, load: message }));
    return this;
  }

  onProcess(processID, callback) {
    if (!(processID in this.onProcess_callbacks)) {
      this.onProcess_callbacks[processID] = [];
    }
    this.onProcess_callbacks[processID].push(callback);
    return this;
  }
}
