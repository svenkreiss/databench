import w3cwebsocket from 'websocket';
const WebSocket = w3cwebsocket;


/**
 * Connection to the backend.
 *
 * The standard template is to create a connection first, then use it to
 * wire all UI elements, to add custom callback functions and at last to run
 * {@link Connection#connect|connect()} to create a WebSocket connection to the backend
 * server (see example below).
 *
 * The other two essential functions to know about are
 * {@link Connection#on|on()} and {@link Connection#emit|emit()}.
 *
 * @example
 * var d = new Databench.Connection();
 * Databench.ui.wire(d);
 * // put custom d.on() methods here
 * d.connect();
 */
class Connection {
  analysisId: string;
  wsUrl: string;
  requestArgs: string;

  errorCB: (message?: string) => void;
  private onCallbacks: any[];
  private _onCallbacksOptimized: any;
  private onProcessCallbacks: any;

  private wsReconnectAttempt: number;
  private wsReconnectDelay: number;
  private socket: WebSocket;
  private socketCheckOpen: number;

  /**
   * @param  {String} [analysisId=null]  Specify an analysis id or null to have one generated.
   *                                     The connection will try to connect to a previously created
   *                                     analysis with that id.
   * @param  {String} [wsUrl=null]       URL of WebSocket endpoint or null to guess it.
   * @param  {String} [requestArgs=null] `search` part of request url or null to take from
   *                                     `window.location.search`.
   */
  constructor(analysisId = null, wsUrl = null, requestArgs = null) {
    this.analysisId = analysisId;
    this.wsUrl = wsUrl || Connection.guessWSUrl();
    this.requestArgs = (requestArgs == null && (typeof window !== 'undefined')) ?
                        window.location.search : requestArgs;

    if (!this.wsUrl) {
      throw Error('Need a wsUrl.');
    }

    this.errorCB = msg => (msg != null ? console.log(`connection error: ${msg}`) : null);
    this.onCallbacks = [];
    this._onCallbacksOptimized = null;
    this.onProcessCallbacks = {};

    this.wsReconnectAttempt = 0;
    this.wsReconnectDelay = 100.0;

    this.socket = null;
    this.socketCheckOpen = null;
  }

  static guessWSUrl() {
    if (typeof location === 'undefined') return null;
    const WSProtocol = location.origin.indexOf('https://') === 0 ? 'wss' : 'ws';
    const path = location.pathname.substring(0, location.pathname.lastIndexOf('/'));
    return `${WSProtocol}://${document.domain}:${location.port}${path}/ws`;
  }

  /** initialize connection */
  connect() {
    this.socket = new WebSocket(this.wsUrl);

    this.socketCheckOpen = setInterval(this.wsCheckOpen.bind(this), 2000);
    this.socket.onopen = this.wsOnOpen.bind(this);
    this.socket.onclose = this.wsOnClose.bind(this);
    this.socket.onmessage = this.wsOnMessage.bind(this);
    return this;
  }

  /** close connection */
  disconnect() {
    this.socket.onclose = null;
    this.socket.close();
    this.socket = null;
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
    setTimeout(this.connect.bind(this), actualDelay);
  }

  wsOnMessage(event) {
    const message = JSON.parse(event.data);

    // connect response
    if (message.signal === '__connect') {
      this.analysisId = message.load.analysis_id;
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
   *
   * The signal can be a simple string (the name for a signal/action), but it
   * can also be an Object of the form `{data: 'current_value'}` which would
   * trigger on `data` actions that are sending a JSON dictionary that contains
   * the key `current_value`. In this case, the value that is
   * given to the callback function is the value assigned to `current_value`.
   *
   * @example
   * d.on('data', value => { console.log(value); });
   * // If the backend sends an action called 'data' with a message
   * // {current_value: 3.0}, this function would log `{current_value: 3.0}`.
   *
   * @example
   * d.on({data: 'current_value'}, value => { console.log(value); });
   * // If the backend sends an action called 'data' with a
   * // message {current_value: 3.0}, this function would log `3.0`.
   * // This callback is not triggered when the message does not contain a
   * // `current_value` key.
   *
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
   * Emit a signal/action to the backend.
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
