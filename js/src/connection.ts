import { w3cwebsocket as WebSocket } from 'websocket';

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
 * Logging across frontend and backend can be done by emitting ``log``,
 * ``warn`` or ``error``, e.g. ``emit('log', 'Hello World')``.
 *
 * @example
 * ~~~
 * var d = new Databench.Connection();
 * Databench.ui.wire(d);
 * // put custom d.on() methods here
 * d.connect();
 * ~~~
 */
export class Connection {
  wsUrl: string;
  requestArgs: string;
  analysisId: string;

  errorCB: (message?: string) => void;
  private onCallbacks: {[field: string]: ((message: any) => void)[]};
  private onProcessCallbacks: {[field: string]: ((status: any) => void)[]};
  private preEmitCallbacks: {[field: string]: ((message: any) => any)[]};

  private wsReconnectAttempt: number;
  private wsReconnectDelay: number;
  private socket: WebSocket;
  private socketCheckOpen: number;

  /**
   * @param  wsUrl        URL of WebSocket endpoint or null to guess it.
   * @param  requestArgs  `search` part of request url or null to take from
   *                      `window.location.search`.
   * @param  analysisId   Specify an analysis id or null to have one generated.
   *                      The connection will try to connect to a previously created
   *                      analysis with that id.
   */
  constructor(wsUrl: string = null, requestArgs: string = null, analysisId: string = null) {
    this.wsUrl = wsUrl || Connection.guessWSUrl();
    this.requestArgs = (requestArgs == null && (typeof window !== 'undefined')) ?
                        window.location.search : requestArgs;
    this.analysisId = analysisId;

    this.errorCB = msg => (msg != null ? console.log(`connection error: ${msg}`) : null);
    this.onCallbacks = {};
    this.onProcessCallbacks = {};
    this.preEmitCallbacks = {};

    this.wsReconnectAttempt = 0;
    this.wsReconnectDelay = 100.0;

    this.socket = null;
    this.socketCheckOpen = null;

    // wire log, warn, error messages into console outputs
    ['log', 'warn', 'error'].forEach(wireSignal => {
      this.on(wireSignal, message => console[wireSignal]('backend: ', message));
      this.preEmit(wireSignal, message => {
        console[wireSignal]('frontend: ', message);
        return message;
      });
    });
  }

  static guessWSUrl(): string {
    if (typeof location === 'undefined') return null;
    const WSProtocol = location.origin.indexOf('https://') === 0 ? 'wss' : 'ws';
    const path = location.pathname.substring(0, location.pathname.lastIndexOf('/'));
    return `${WSProtocol}://${document.domain}:${location.port}${path}/ws`;
  }

  /** initialize connection */
  connect(): Connection {
    if (!this.wsUrl) {
      throw Error('Need a wsUrl.');
    }

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

    if (this.wsReconnectAttempt > 5) {
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

  /**
   * Trigger all callbacks for this signal with this message.
   * @param signal  Name of the signal to trigger.
   * @param message Payload for the triggered signal.
   */
  trigger(signal: string, message: any = null) {
    this.onCallbacks[signal].forEach(cb => cb(message));
  }

  wsOnMessage(event: {data: string}) {
    const message = JSON.parse(event.data);

    // connect response
    if (message.signal === '__connect') {
      this.analysisId = message.load.analysis_id;
    }

    // processes
    if (message.signal === '__process') {
      const id = message.load.id;
      const status = message.load.status;
      this.onProcessCallbacks[id].forEach(cb => cb(status));
    }

    // normal message
    if (message.signal in this.onCallbacks) {
      this.trigger(message.signal, message.load);
    }
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
   * ~~~
   * d.on('data', value => { console.log(value); });
   * // If the backend sends an action called 'data' with a message
   * // {current_value: 3.0}, this function would log `{current_value: 3.0}`.
   * ~~~
   *
   * @example
   * ~~~
   * d.on({data: 'current_value'}, value => { console.log(value); });
   * // If the backend sends an action called 'data' with a
   * // message {current_value: 3.0}, this function would log `3.0`.
   * // This callback is not triggered when the message does not contain a
   * // `current_value` key.
   * ~~~
   *
   * @param  signal    Signal name to listen for.
   * @param  callback  A callback function that takes the attached data.
   * @return           this
   */
  on(signal: string|{[field: string]: string}, callback: (message: any) => void): Connection {
    if (typeof signal === 'object') {
      this._on_object(signal, callback);
      return this;
    }

    if (!(signal in this.onCallbacks)) this.onCallbacks[signal] = [];
    this.onCallbacks[signal].push(callback);
    return this;
  }

  _on_object(signal: {[field: string]: string}, callback: (message: any) => void): Connection {
    Object.keys(signal).forEach(signalName => {
      const entryName = signal[signalName];
      const filteredCallback = data => {
        if (!data.hasOwnProperty(entryName)) return;
        callback(data[entryName]);
      };
      this.on(signalName, filteredCallback);
    });

    return this;
  }

  /**
   * Set a pre-emit hook.
   * @param signalName  A signal name.
   * @param callback    Callback function.
   * @return            this
   */
  preEmit(signalName: string, callback: (message: any) => any): Connection {
    if (!(signalName in this.preEmitCallbacks)) this.preEmitCallbacks[signalName] = [];
    this.preEmitCallbacks[signalName].push(callback);
    return this;
  }

  /**
   * Emit a signal/action to the backend.
   * @param  signalName  A signal name. Usually an action name.
   * @param  message     Payload attached to the action.
   * @return             this
   */
  emit(signalName: string, message?): Connection {
    // execute preEmit hooks before sending message to backend
    if (signalName in this.preEmitCallbacks) {
      this.preEmitCallbacks[signalName].forEach(cb => {
        message = cb(message);
      });
    }

    // socket will never be open
    if (this.socket == null) return this;

    // socket is not open yet
    if (this.socket.readyState !== this.socket.OPEN) {
      setTimeout(() => this.emit(signalName, message), 5);
      return this;
    }

    // send to backend
    this.socket.send(JSON.stringify({ signal: signalName, load: message }));
    return this;
  }

  onProcess(processID: number, callback): Connection {
    if (!(processID in this.onProcessCallbacks)) {
      this.onProcessCallbacks[processID] = [];
    }
    this.onProcessCallbacks[processID].push(callback);
    return this;
  }
}


/**
 * Create a Connection and immediately connect to it.
 *
 * This is a shorthand for
 * ~~~
 * new Connection(wsUrl, requestArgs, analysisId).connect();
 * ~~~
 *
 * Use this function in tests where you know that connect() will not trigger
 * any callbacks that you should listen to. In regular code, it is better
 * to define all ``on`` callbacks before calling ``connect()`` and so this
 * shorthand should not be used.
 *
 * @param  wsUrl        URL of WebSocket endpoint or null to guess it.
 * @param  requestArgs  `search` part of request url or null to take from
 *                      `window.location.search`.
 * @param  analysisId   Specify an analysis id or null to have one generated.
 *                      The connection will try to connect to a previously created
 *                      analysis with that id.
 */
export function connect(wsUrl: string = null, requestArgs: string = null, analysisId: string = null) {
  return new Connection(wsUrl, requestArgs, analysisId).connect();
}
