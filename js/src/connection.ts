// type definitions on DefinitelyTyped are missing the w3cwebsocket definitions
declare module 'websocket' {
  export class w3cwebsocket {  // tslint:disable-line
    constructor(url: string);

    onopen(): void;
    onclose: (() => void) | null;
    onmessage(event: {data: string}): void;

    send(message: string): void;
    close(): void;

    CONNECTING: string;
    OPEN: string;
    readyState: string;
  }
}

import { w3cwebsocket as WebSocket } from 'websocket';

/**
 * Connection to the backend.
 *
 * The standard template is to create a connection first, then use it to
 * wire all UI elements, to add custom callback functions and at last to run
 * [[Connection.connect]] to create a WebSocket connection to the backend
 * server (see example below).
 *
 * The other two essential functions to know about are
 * [[Connection.on]] and [[Connection.emit]].
 *
 * Logging across frontend and backend can be done by emitting `log`,
 * `warn` or `error`, e.g. `emit('log', 'Hello World')`.
 *
 * ```js
 * var databench = new Databench.Connection();
 * Databench.ui.wire(databench);
 *
 *
 * // put custom databench.on() methods here
 *
 *
 * databench.connect();
 * ```
 */
export class Connection {
  wsUrl: string;
  requestArgs?: string;
  analysisId?: string;
  databenchBackendVersion?: string;
  analysesVersion?: string;

  errorCB: (message?: string) => void;
  private onCallbacks: {[field: string]: ((message: any, signal?: string) => void)[]};
  private onProcessCallbacks: {[field: string]: ((status: any) => void)[]};
  private preEmitCallbacks: {[field: string]: ((message: any) => any)[]};
  private connectCallback: (connection: Connection) => void;

  private wsReconnectAttempt: number;
  private wsReconnectDelay: number;
  private socket?: WebSocket;
  private socketCheckOpen?: number;

  /**
   * @param  wsUrl        URL of WebSocket endpoint or undefined to guess it.
   * @param  requestArgs  `search` part of request url or undefined to take from
   *                      `window.location.search`.
   * @param  analysisId   Specify an analysis id or undefined to have one generated.
   *                      The connection will try to connect to a previously created
   *                      analysis with that id.
   */
  constructor(wsUrl?: string, requestArgs?: string, analysisId?: string) {
    this.wsUrl = wsUrl || Connection.guessWSUrl();
    this.requestArgs = (!requestArgs && (typeof window !== 'undefined')) ?
                        window.location.search : requestArgs;
    this.analysisId = analysisId;

    this.errorCB = msg => (msg != null ? console.log(`connection error: ${msg}`) : null);
    this.onCallbacks = {};
    this.onProcessCallbacks = {};
    this.preEmitCallbacks = {};
    this.connectCallback = connection => {};

    this.wsReconnectAttempt = 0;
    this.wsReconnectDelay = 100.0;

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
    if (typeof location === 'undefined') return '';
    const WSProtocol = location.origin.indexOf('https://') === 0 ? 'wss' : 'ws';
    const path = location.pathname.substring(0, location.pathname.lastIndexOf('/'));
    return `${WSProtocol}://${document.domain}:${location.port}${path}/ws`;
  }

  /** initialize connection */
  connect(callback?: (connection: Connection) => void): Connection {
    if (!this.wsUrl) throw Error('Need a wsUrl.');
    this.connectCallback = callback ? callback : () => this;

    this.socket = new WebSocket(this.wsUrl);
    this.socketCheckOpen = setInterval(this.wsCheckOpen.bind(this), 2000);
    this.socket.onopen = this.wsOnOpen.bind(this);
    this.socket.onclose = this.wsOnClose.bind(this);
    this.socket.onmessage = this.wsOnMessage.bind(this);
    return this;
  }

  /** close connection */
  disconnect() {
    if (this.socketCheckOpen) {
      clearInterval(this.socketCheckOpen);
      this.socketCheckOpen = undefined;
    }
    if (this.socket) {
      this.socket.onclose = null;
      this.socket.close();
      this.socket = undefined;
    }
  }

  wsCheckOpen() {
    if (!this.socket) return;

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

    if (this.socketCheckOpen) {
      clearInterval(this.socketCheckOpen);
      this.socketCheckOpen = undefined;
    }
  }

  wsOnOpen() {
    if (!this.socket) return;

    this.wsReconnectAttempt = 0;
    this.wsReconnectDelay = 100.0;
    this.errorCB();  // clear errors
    this.socket.send(JSON.stringify({
      __connect: this.analysisId ? this.analysisId : null,
      __request_args: this.requestArgs,  // eslint-disable-line camelcase
    }));
  }

  wsOnClose() {
    if (this.socketCheckOpen) {
      clearInterval(this.socketCheckOpen);
      this.socketCheckOpen = undefined;
    }

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
  trigger(signal: string, message?: any) {
    this.onCallbacks[signal].forEach(cb => cb(message, signal));
  }

  wsOnMessage(event: {data: string}) {
    const message = JSON.parse(event.data);

    // connect response
    if (message.signal === '__connect') {
      this.analysisId = message.load.analysis_id;
      this.databenchBackendVersion = message.load.databench_backend_version;

      const newVersion = message.load.analyses_version;
      if (this.analysesVersion && this.analysesVersion !== newVersion) {
        location.reload();
      }
      this.analysesVersion = newVersion;
      this.connectCallback(this);
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
   * ~~~
   * d.on('data', value => { console.log(value); });
   * // If the backend sends an action called 'data' with a message
   * // {current_value: 3.0}, this function would log `{current_value: 3.0}`.
   * ~~~
   *
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
   */
  on(signal: string|{[field: string]: string}|{[field: string]: RegExp},
     callback: (message: any, key?: string) => void): Connection {
    if (typeof signal === 'object') {
      this._on_object(signal, callback);
      return this;
    }

    if (!(signal in this.onCallbacks)) this.onCallbacks[signal] = [];
    this.onCallbacks[signal].push(callback);
    return this;
  }

  /**
   * Listen for a signal once.
   *
   * Similar to [on] but returns a `Promise` instead of taking a callback.
   * This is mostly useful for unit tests.
   *
   * @param signal Signal name to listen for.
   */
  once(signal: string|{[field: string]: string}|{[field: string]: RegExp}): Promise<{message: any, key?: string}> {
    return new Promise(resolve => {
      this.on(signal, resolve);
    });
  }

  _on_object(signal: {[field: string]: string}|{[field: string]: RegExp},
             callback: (message: any, key?: string) => void): Connection {
    Object.keys(signal).forEach(signalName => {
      const entryName = signal[signalName];
      const filteredCallback = (data: any, signalName: string) => {
        Object.keys(data).forEach(dataKey => {
          if (dataKey.match(entryName) === null) return;
          callback(data[dataKey], dataKey);
        });
      };
      this.on(signalName, filteredCallback);
    });

    return this;
  }

  /**
   * Set a pre-emit hook.
   * @param signalName  A signal name.
   * @param callback    Callback function.
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
   */
  emit(signalName: string, message?: any): Connection {
    // execute preEmit hooks before sending message to backend
    if (signalName in this.preEmitCallbacks) {
      this.preEmitCallbacks[signalName].forEach(cb => {
        message = cb(message);
      });
    }

    // socket will never be open
    if (!this.socket) return this;

    // socket is not open yet
    if (this.socket.readyState !== this.socket.OPEN) {
      setTimeout(() => this.emit(signalName, message), 5);
      return this;
    }

    // send to backend
    this.socket.send(JSON.stringify({ signal: signalName, load: message }));
    return this;
  }

  onProcess(processID: number, callback: (message: any) => void): Connection {
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
 * Use this function in tests where you know that `connect()` will not trigger
 * any callbacks that you should listen to. In regular code, it is better
 * to define all `on` callbacks before calling `connect()` and so this
 * shorthand should not be used.
 *
 * @param wsUrl       URL of WebSocket endpoint or undefined to guess it.
 * @param requestArgs `search` part of request url or undefined to take from
 *                     `window.location.search`.
 * @param analysisId  Specify an analysis id or undefined to have one generated.
 *                    The connection will try to connect to a previously created
 *                    analysis with that id.
 * @param callback    Called when connection is established.
 */
export function connect(wsUrl?: string, requestArgs?: string, analysisId?: string, callback?: (connection: Connection) => void) {
  return new Connection(wsUrl, requestArgs, analysisId).connect(callback);
}

/**
 * Attach to a backend.
 *
 * Similar to [connect](globals.html#connect). Instead of a callback parameter, it
 * returns a Promise that resolves to a [[Connection]] instance once the connection is
 * established.
 *
 * @param wsUrl       URL of WebSocket endpoint or undefined to guess it.
 * @param requestArgs `search` part of request url or undefined to take from
 *                    `window.location.search`.
 * @param analysisId  Specify an analysis id or undefined to have one generated.
 *                    The connection will try to connect to a previously created
 *                    analysis with that id.
 */
export function attach(wsUrl?: string, requestArgs?: string, analysisId?: string): Promise<Connection> {
  const connection = new Connection(wsUrl, requestArgs, analysisId);
  return new Promise((resolve) => connection.connect(resolve));
}
