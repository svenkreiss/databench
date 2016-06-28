let WebSocket;
if (typeof WebSocket === 'undefined') {
  WebSocket = require('websocket').w3cwebsocket;  // eslint-disable-line
}

/** Connection to the backend. */
class Connection {
  /**
   * Create a connection to the backend with a WebSocket.
   * @param  {String} [analysisId=null]  Specify an analysis id or null to have one generated.
   * @param  {String} [wsUrl=null]       URL of WebSocket endpoint or null to guess it.
   * @param  {String} [requestArgs=null] `search` part of request url or null to take from
   *                                     `window.location.search`.
   */
  constructor(analysisId = null, wsUrl = null, requestArgs = null) {
    this.analysisId = analysisId;
    this.wsUrl = wsUrl || Connection.guessWSUrl();
    this.requestArgs = (requestArgs == null && (typeof window !== 'undefined')) ?
                        window.location.search : requestArgs;

    this.errorCB = msg => (msg != null ? console.log(`connection error: ${msg}`) : null);
    this.onCallbacks = [];
    this._onCallbacksOptimized = null;
    this.onProcessCallbacks = {};

    this.wsReconnectAttempt = 0;
    this.wsReconnectDelay = 100.0;

    this.socket = null;
    this.socketCheckOpen = null;

    // bind methods
    this.connect = this.connect.bind(this);
    this.wsCheckOpen = this.wsCheckOpen.bind(this);
    this.wsOnOpen = this.wsOnOpen.bind(this);
    this.wsOnClose = this.wsOnClose.bind(this);
    this.wsOnMessage = this.wsOnMessage.bind(this);
    this.optimizeOnCallbacks = this.optimizeOnCallbacks.bind(this);
    this.on = this.on.bind(this);
    this.emit = this.emit.bind(this);
    this.onProcess = this.onProcess.bind(this);
  }

  static guessWSUrl() {
    let WSProtocol = 'ws';
    if (location.origin.startsWith('https://')) WSProtocol = 'wss';

    const path = location.pathname.substring(0, location.pathname.lastIndexOf('/'));
    return `${WSProtocol}://${document.domain}:${location.port}${path}/ws`;
  }

  /** initialize connection */
  connect() {
    this.socket = new WebSocket(this.wsUrl);

    this.socketCheckOpen = setInterval(this.wsCheckOpen, 2000);
    this.socket.onopen = this.wsOnOpen;
    this.socket.onclose = this.wsOnClose;
    this.socket.onmessage = this.wsOnMessage;
    return this;
  }

  wsCheckOpen() {
    if (this.socket.readyState === this.socket.CONNECTING) {
      return;
    }
    if (this.socket.readyState !== this.socket.OPEN) {
      this.errorCB(
        'Connection could not be opened. ' +
        'Please <a href="javascript:location.reload(true);" ' +
        'class="alert-link">reload</a> this page to try again.'
      );
    }
    clearInterval(this.socketCheckOpen);
  }

  wsOnOpen() {
    this.wsReconnectAttempt = 0;
    this.wsReconnectDelay = 100.0;
    this.errorCB();  // clear errors
    this.socket.send(JSON.stringify({
      __connect: this.analysisId,
      __request_args: this.requestArgs,  // eslint-disable-line camelcase
    }));
  }

  wsOnClose() {
    clearInterval(this.socketCheckOpen);

    this.wsReconnectAttempt += 1;
    this.wsReconnectDelay *= 2;

    if (this.wsReconnectAttempt > 3) {
      this.errorCB(
        'Connection closed. ' +
        'Please <a href="javascript:location.reload(true);" ' +
        'class="alert-link">reload</a> this page to reconnect.'
      );
      return;
    }

    const actualDelay = 0.7 * this.wsReconnectDelay + 0.3 * Math.random() *
                        this.wsReconnectDelay;
    console.log(`WebSocket reconnect attempt ${this.wsReconnectAttempt} ` +
                `in ${actualDelay.toFixed(0)}ms.`);
    setTimeout(this.connect, actualDelay);
  }

  wsOnMessage(event) {
    const message = JSON.parse(event.data);

    // connect response
    if (message.signal === '__connect') {
      this.analysisId = message.load.analysisId;
    }

    // processes
    if (message.signal === '__process') {
      const id = message.load.id;
      const status = message.load.status;
      this.onProcessCallbacks[id].map(cb => cb(status));
    }

    // normal message
    if (this._onCallbacksOptimized === null) this.optimizeOnCallbacks();
    if (message.signal in this._onCallbacksOptimized) {
      this._onCallbacksOptimized[message.signal].map(cb => cb(message.load));
    }
  }

  optimizeOnCallbacks() {
    this._onCallbacksOptimized = {};
    this.onCallbacks.forEach(({ signal, callback }) => {
      if (typeof signal === 'string') {
        if (!(signal in this._onCallbacksOptimized)) {
          this._onCallbacksOptimized[signal] = [];
        }
        this._onCallbacksOptimized[signal].push(callback);
      } else if (typeof signal === 'object') {
        Object.keys(signal).forEach(signalName => {
          const entryName = signal[signalName];
          const filteredCallback = data => {
            if (data.hasOwnProperty(entryName)) {
              callback(data[entryName]);
            }
          };

          if (!(signalName in this._onCallbacksOptimized)) {
            this._onCallbacksOptimized[signalName] = [];
          }

          // only use the filtered callback if the entry was not empty
          if (entryName) {
            this._onCallbacksOptimized[signalName].push(filteredCallback);
          } else {
            this._onCallbacksOptimized[signalName].push(callback);
          }
        });
      }
    });
  }

  /**
   * Register a callback that listens for a signal.
   * @param  {string|Object}   signal   Signal name to listen for.
   * @param  {Function}        callback A callback function that takes the attached data.
   * @return {Connection}      this
   */
  on(signal, callback) {
    this.onCallbacks.push({ signal, callback });
    this._onCallbacksOptimized = null;
    return this;
  }

  /**
   * Emit a signal to the backend.
   * @param  {string}                   signalName A signal name. Usually an action name.
   * @param  {string|Object|Array|null} message    Payload attached to the action.
   * @return {Connection}                          this
   */
  emit(signalName, message) {
    if (this.socket == null || this.socket.readyState !== this.socket.OPEN) {
      setTimeout(() => this.emit(signalName, message), 5);
      return this;
    }
    this.socket.send(JSON.stringify({ signal: signalName, load: message }));
    return this;
  }

  onProcess(processID, callback) {
    if (!(processID in this.onProcessCallbacks)) {
      this.onProcessCallbacks[processID] = [];
    }
    this.onProcessCallbacks[processID].push(callback);
    return this;
  }
}

export { Connection };
