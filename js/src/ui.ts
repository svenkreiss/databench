/**
 * This is a basic set of UI elements to create analyses without having to add
 * frontend frameworks like Angular or React.
 *
 * @module ui
 */

export interface HTMLDatabenchElement {
  databenchUI: UIElement;
  classList: any;
  addEventListener: any;
  innerHTML: string;
  innerText: string;
}

/**
 * Abstract class for user interface elements which provides general helpers
 * to determine the action name from an HTML tag and a way to modify the message
 * that is sent with actions of wired elements.
 *
 * The constructor adds the variables `actionName` and `wireSignal` using
 * {@link module:ui~UIElement.determineActionName|determineActionName()} and
 * {@link module:ui~UIElement.determineWireSignal|determineWireSignal()}
 * respectively.
 * It also adds `this` UI element to the DOM node at `databenchUI`.
 */
export class UIElement {
  node: HTMLDatabenchElement;
  actionName: string;
  wireSignal: string|any;

  /**
   * @param  {HTMLElement} node An HTML element.
   */
  constructor(node) {
    this.node = node;
    this.node.databenchUI = this;

    this.actionName = UIElement.determineActionName(node);
    this.wireSignal = UIElement.determineWireSignal(node);
  }

  /**
   * Formats the payload of an action.
   * @param  {any} value Original payload.
   * @return {any}       Modified payload.
   */
  actionFormat(value) {
    return value;
  }

  /**
   * Determine the name of the action that should be associated with the node.
   *
   * This can be forced to be `null` by adding a `data-skipwire=true` attribute
   * to the HTML tag. If that is not found, the action name is determined from
   * the tag's `data-action`, `name` or `id` attribute (in that order).
   *
   * @param  {HTMLElement} node A HTML element.
   * @return {string}      Name of action or null.
   */
  static determineActionName(node) {
    // determine action name from HTML DOM
    let action = null;

    if (node.dataset.skipwire === 'true' ||
      node.dataset.skipwire === 'TRUE' ||
      node.dataset.skipwire === '1') {
      return null;
    }

    if (node.dataset.action) {
      action = node.dataset.action;
    } else if (node.getAttribute('name')) {
      action = node.getAttribute('name');
    } else if (node.getAttribute('id')) {
      action = node.getAttribute('id');
    }

    return action;
  }

  /**
   * Determine the name of the signal that should be listened to from the backend.
   *
   * If the HTML tag as a `data-skipwire=true` attribute, this is forced to be
   * null. Otherwise the signal name is determined from the `data-signal`,
   * `data-action`, `name` or `id` attribute (in that order.)
   * For all attributes apart from `data-signal`, the value is wrapped in an
   * object like `{ data: value-of-attribute }`. The `data-signal` value
   * can contain a `:` which will be used to create an object as well. That means
   * that `data-signal="data:myvalue"` gives the same result as `data-action="myvalue"`.
   *
   * @param  {HTMLElement} node A HTML element.
   * @return {string}           Name of a signal or null.
   */
  static determineWireSignal(node) {
    // determine signal name from HTML DOM
    let signal = null;

    if (node.dataset.skipwire === 'true' ||
      node.dataset.skipwire === 'TRUE' ||
      node.dataset.skipwire === '1') {
      return null;
    }

    if (node.dataset.signal) {
      signal = node.dataset.signal;
      if (signal.indexOf(':') >= 1) {
        const [key, value] = signal.split(':', 2);
        signal = { [key]: value };
      }
    } else if (node.dataset.action) {
      signal = { data: node.dataset.action };
    } else if (node.getAttribute('name')) {
      signal = { data: node.getAttribute('name') };
    } else if (node.getAttribute('id')) {
      signal = { data: node.getAttribute('id') };
    }

    return signal;
  }
}

/**
 * Shows all `console.log()` messages and `log` actions from backend.
 *
 * Usually wired to a `<pre id="log">` element.
 */
export class Log extends UIElement {
  consoleFnName: string;
  limitNumber: number;
  limitLength: number;
  _messages: string[][];

  /**
   * @param  {HTMLElement} node     Primary node.
   * @param  {String} [consoleFnName='log'] Name of console method to replace.
   * @param  {Number} [limitNumber=20]      Maximum number of messages to show.
   * @param  {Number} [limitLength=250]     Maximum length of a message.
   */
  constructor(node, consoleFnName = 'log', limitNumber = 20, limitLength = 250) {
    super(node);

    this.consoleFnName = consoleFnName;
    this.limitNumber = limitNumber;
    this.limitLength = limitLength;
    this._messages = [];

    // more sensible default for this case
    this.wireSignal = { log: null };

    // capture events from frontend
    const _consoleFnOriginal = console[consoleFnName];
    console[consoleFnName] = message => {
      this.add(message, 'frontend');
      _consoleFnOriginal.apply(console, [message]);
    };
  }

  render() {
    while (this._messages.length > this.limitNumber) this._messages.shift();

    this.node.innerText = this._messages
      .map(m => m.join(''))
      .map(m => ((m.length > this.limitLength)
                 ? `${m.substr(0, this.limitLength)} ...`
                 : m))
      .join('\n');

    return this;
  }

  add(message, source = 'unknown') {
    const msg = typeof message === 'string' ? message : JSON.stringify(message);
    const paddedSource = Array(Math.max(0, 8 - source.length)).join(' ') + source;
    this._messages.push([`${paddedSource}: ${msg}`]);
    this.render();
    return this;
  }

  /** Wire all logs. */
  static wire(conn, root?, id = 'log', source = 'backend', consoleFnName = 'log',
              limitNumber = 20, limitLength = 250) {
    if (root === undefined) root = document;
    const node = root.getElementById(id);
    if (node == null) return;
    if (UIElement.determineActionName(node) == null) return;

    console.log('Wiring log to ', node, `with id=${id}.`);
    const l = new Log(node, consoleFnName, limitNumber, limitLength);
    conn.on(l.wireSignal, message => l.add(message, source));
    return;
  }
}


/**
 * Visual representation of alerts like connection failures.
 *
 * Usually wired to a `<div id="databench-alerts">` element.
 */
export class StatusLog extends UIElement {
  formatter: (message: string, count: number) => string;
  _messages: { [message: string]: number };

  /**
   * @param  {HTMLElement} node      HTML node.
   * @param  {function}    formatter Formats a message and a count to a string.
   */
  constructor(node, formatter = StatusLog.defaultAlert) {
    super(node);

    this.formatter = formatter;
    this._messages = {};

    // to avoid confusion, void meaningless parent variable
    this.wireSignal = null;
  }

  /**
   * The default formatter function
   * @param  {string} msg   A message.
   * @param  {number} count Count of the message.
   * @return {string}       HTML formatted version of the inputs.
   */
  static defaultAlert(msg, count) {
    const countFormat = count <= 1 ? '' : `<b>(${count})</b> `;
    return `<div class="alert alert-danger">${countFormat}${msg}</div>`;
  }

  render() {
    const formatted = Object.getOwnPropertyNames(this._messages)
      .map((m: string) => this.formatter(m, this._messages[m]));
    this.node.innerHTML = formatted.join('\n');
    return this;
  }

  add(message) {
    if (message == null) {
      this._messages = {};
      return this;
    }
    const msg = typeof message === 'string' ? message : JSON.stringify(message);

    if (this._messages[msg] !== undefined) {
      this._messages[msg] += 1;
    } else {
      this._messages[msg] = 1;
    }
    this.render();
    return this;
  }

  /** Wire all status logs. */
  static wire(conn, root?, id = 'databench-alerts', formatter = StatusLog.defaultAlert) {
    if (root === undefined) root = document;
    const node = root.getElementById(id);
    if (node == null) return;
    if (UIElement.determineActionName(node) == null) return;

    console.log('Wiring status log', node, `to element with id=${id}.`);
    const l = new StatusLog(node, formatter);
    conn.errorCB = l.add.bind(l);
  }
}

export enum ButtonState {
  Idle = 1,
  Active,
}

/**
 * A button, and usually wired to any `<button>` with an action name.
 *
 * This button also binds to process IDs of the backend. That means
 * that the button is disabled (using the CSS class `disabled`) while the
 * backend is processing the action that got started when it was clicked.
 * A simple example is below.
 *
 * @example
 * ~~~
 * // in index.html, add:
 * <button data-action="run">Run</button>
 *
 * // in analysis.py, add:
 * def on_run(self):
 *     """Run when button is pressed."""
 *     pass
 *
 * // In this form, Databench finds the button automatically and connects it
 * // to the backend. No additional JavaScript code is required.
 * ~~~
 */
export class Button extends UIElement {
  _state: ButtonState;

  /**
   * @param  {HTMLElement} node DOM node to connect.
   */
  constructor(node) {
    super(node);

    this._state = ButtonState.Idle;

    this.node.addEventListener('click', this.click.bind(this), false);
  }

  /**
   * Called on click events. When a button is wired, this function is overwritten
   * with the actual function that is triggered on click events.
   * @param  {int} processID a random id for the process that could be started
   */
  clickCB(processID) {
    return console.log(`click on ${this.node} with ${processID}`);
  }

  render() {
    switch (this._state) {
      case ButtonState.Active:
        this.node.classList.add('disabled');
        break;
      default:
        this.node.classList.remove('disabled');
    }
    return this;
  }

  click() {
    if (this._state !== ButtonState.Idle) return this;

    const processID = Math.floor(Math.random() * 0x100000);
    this.clickCB(processID);
    return this;
  }

  state(s) {
    if (s !== ButtonState.Idle && s !== ButtonState.Active) return this;

    this._state = s;
    this.render();
    return this;
  }

  /** Wire all buttons. */
  static wire(conn, root?) {
    if (root === undefined) root = document;

    [].slice.call(root.getElementsByTagName('BUTTON'), 0)
      .filter(node => (<HTMLDatabenchElement>node).databenchUI === undefined)
      .filter(node => UIElement.determineActionName(node) !== null)
      .forEach(node => {
        const b = new Button(node);
        console.log('Wiring button', node, `to action ${b.actionName}.`);

        // set up click callback
        b.clickCB = (processID) => {
          // set up process callback
          conn.onProcess(processID, status => b.state(
            // map process status to state
            { start: ButtonState.Active, end: ButtonState.Idle }[status]
          ));

          conn.emit(b.actionName, b.actionFormat({
            __process_id: processID,  // eslint-disable-line camelcase
          }));
        };
      });
  }
}


/**
 * Data bound text elements.
 *
 * Wired to ``<span>``, ``<p>``, ``<div>``, ``<i>`` and ``<b>`` tags with a
 * ``data-action`` attribute specifying the action name.
 */
export class Text extends UIElement {
  /**
   * Format the value.
   * @param  {any} value Value as represented in the backend.
   * @return {string}       Formatted representation of the value.
   */
  formatFn(value) {
    return value;
  }

  /** Reads and sets the value. */
  value(v) {
    if (v === undefined) return this.node.innerHTML;

    this.node.innerHTML = this.formatFn(v || '');
    return this;
  }

  /**
   * Wire all text.
   * @param  {Connection} conn Connection to use.
   */
  static wire(conn, root?) {
    if (root === undefined) root = document;

    [].concat(
      [].slice.call(root.getElementsByTagName('SPAN'), 0),
      [].slice.call(root.getElementsByTagName('P'), 0),
      [].slice.call(root.getElementsByTagName('DIV'), 0),
      [].slice.call(root.getElementsByTagName('I'), 0),
      [].slice.call(root.getElementsByTagName('B'), 0),
    )
      .filter(node => (<HTMLDatabenchElement>node).databenchUI === undefined)
      .filter(node => (<HTMLElement>node).dataset['action'] !== undefined)
      .filter(node => UIElement.determineActionName(node) !== null)
      .forEach(node => {
        const t = new Text(node);
        console.log('Wiring text', node, `to action ${t.actionName}.`);

        // handle events from backend
        conn.on(t.wireSignal, message => t.value(message));
      });
  }
}


/** Make an `<input[type='text']>` with an action name interactive. */
export class TextInput extends UIElement {
  node: HTMLInputElement & HTMLDatabenchElement;
  _triggerOnKeyUp: boolean;

  /**
   * @param {HTMLElement} node The node to connect.
   */
  constructor(node) {
    super(node);

    this._triggerOnKeyUp = false;

    this.node.addEventListener('change', this.change.bind(this), false);
  }

  /**
   * Format the value.
   * @param  {any}    value Value as represented in the backend.
   * @return {string}       Formatted representation of the value.
   */
  formatFn(value) {
    return value;
  }

  /**
   * Callback that is triggered on frontend changes.
   * @param  {any} value A formatted action.
   */
  changeCB(value) {
    return console.log(`change of ${this.node}: ${value}`);
  }

  change() {
    return this.changeCB(this.actionFormat(this.value()));
  }

  /**
   * The default is `false`, which means that the callback is only triggered on
   * `change` events (i.e. pressing enter or unfocusing the element).
   * Setting this to true will trigger on every `keyup` event of this element.
   *
   * @param  {boolean}   v Whether to trigger on `keyup` events. Default is true.
   * @return {TextInput}   self
   */
  triggerOnKeyUp(v) {
    if (v !== false && !this._triggerOnKeyUp) {
      this.node.addEventListener('keyup', this.change.bind(this), false);
      this._triggerOnKeyUp = true;
    }

    if (v === false && this._triggerOnKeyUp) {
      this.node.removeEventListener('keyup', this.change.bind(this), false);
      this._triggerOnKeyUp = false;
    }

    return this;
  }

  /** Reads and sets the value. */
  value(v?) {
    if (v === undefined) return this.node.value;

    this.node.value = this.formatFn(v || '');
    return this;
  }

  /** Wire all text inputs. */
  static wire(conn, root?) {
    if (root === undefined) root = document;

    [].slice.call(root.getElementsByTagName('INPUT'), 0)
      .filter(node => (<HTMLDatabenchElement>node).databenchUI === undefined)
      .filter(node => node.getAttribute('type') === 'text')
      .filter(node => UIElement.determineActionName(node) !== null)
      .forEach(node => {
        const t = new TextInput(node);
        console.log('Wiring text input', node, `to action ${t.actionName}.`);

        // handle events from frontend
        t.changeCB = message => conn.emit(t.actionName, message);

        // handle events from backend
        conn.on(t.wireSignal, message => t.value(message));
      });
  }
}


/**
 * Make all `<input[type='range']>` with an action name interactive.
 *
 * @example
 * ~~~
 * // in index.html, add:
 * <label for="samples">Samples:</label>
 * <input type="range" id="samples" value="1000" min="100" max="10000" step="100" />
 *
 * // in analysis.py, add:
 * def on_samples(self, value):
 *     """Sets the number of samples to generate per run."""
 *     self.data['samples'] = value
 *
 * // The Python code is for illustration only and can be left out as this is
 * // the default behavior.
 * ~~~
 */
export class Slider extends UIElement {
  node: HTMLInputElement & HTMLDatabenchElement;
  labelNode: HTMLElement;
  labelHtml: string;

  /**
   * @param  {HTMLElement}  node      DOM node to bind.
   * @param  {HTMLElement?} labelNode DOM node label that corresponds to the slider.
   */
  constructor(node, labelNode) {
    super(node);

    this.labelNode = labelNode;
    this.labelHtml = labelNode ? labelNode.innerHTML : null;

    this.node.addEventListener('input', this.render.bind(this), false);
    this.node.addEventListener('change', this.change.bind(this), false);
    this.render();
  }

  /**
   * Callback with changes to the slider value.
   * @param  {Number} value   Value from a sliderToValue() transform.
   */
  changeCB(value) {
    return console.log(`slider value change: ${value}`);
  }

  /**
   * Transform a backend value to a slider value.
   * @param  {number} value Value as stored in backend.
   * @return {int}          Value for the HTML range element.
   */
  valueToSlider(value) {
    return value;
  }

  /**
   * Transform a value from the HTML range element to a value that should be stored.
   * @param  {int}    s Value from HTML range element.
   * @return {number}   Value to store.
   */
  sliderToValue(s) {
    return s;
  }

  /**
   * How a value should be represented.
   * For example, this can add units or convert from radians to degrees.
   * @param  {number}         value Input value as it is stored in the backend.
   * @return {string|number}        Representation of a value.
   */
  formatFn(value) {
    return value;
  }

  render() {
    const v = this.value();
    if (this.labelNode) {
      this.labelNode.innerHTML = `${this.labelHtml} ${this.formatFn(v)}`;
    }
    return this;
  }

  /** Reads and sets the value. */
  value(v?) {
    if (v === undefined) {
      return this.sliderToValue(parseFloat(this.node.value));
    }

    const newSliderValue = this.valueToSlider(v);
    if (this.node.value === newSliderValue) return this;

    this.node.value = newSliderValue;
    this.render();
    return this;
  }

  change() {
    return this.changeCB(this.actionFormat(this.value()));
  }

  /** Find all labels for slider elements. */
  static labelsForSliders(root) {
    let map: { [inputname: string]: HTMLLabelElement } = {};
    [].slice.call(root.getElementsByTagName('LABEL'), 0)
      .filter(label => (<HTMLLabelElement>label).htmlFor)
      .forEach(label => {
        map[(<HTMLLabelElement>label).htmlFor] = label;
      });
    return map;
  }

  /** Wire all sliders. */
  static wire(conn, root?) {
    if (root === undefined) root = document;
    const lfs = this.labelsForSliders(root);

    [].slice.call(root.getElementsByTagName('INPUT'), 0)
      .filter(node => (<HTMLDatabenchElement>node).databenchUI === undefined)
      .filter(node => (<HTMLElement>node).getAttribute('type') === 'range')
      .filter(node => UIElement.determineActionName(node) !== null)
      .forEach(node => {
        const slider = new Slider(node, lfs[node.id]);
        console.log('Wiring slider', node, `to action ${slider.actionName}.`);

        // handle events from frontend
        slider.changeCB = message => conn.emit(slider.actionName, message);

        // handle events from backend
        conn.on(slider.wireSignal, message => slider.value(message));
      });
  }
}


/**
 * Connect an `<img>` with a signal name to the backend.
 *
 * The signal message is placed directly into the `src` attribute of the image
 * tag. For matplotlib, that formatting can be done with the utility function
 * `fig_to_src()` (see example below).
 *
 * @example
 * ~~~
 * // in index.html, add
 * <img alt="my plot" data-signal="mpl" />
 *
 * // in analysis.py, add
 * import matplotlib.pyplot as plt
 * ...
 * fig = plt.figure()
 * ...
 * self.emit('mpl', databench.fig_to_src(fig))
 * ~~~
 */
export class Image extends UIElement {
  node: HTMLImageElement & HTMLDatabenchElement;

  /** Reads and sets the value. */
  value(v) {
    if (v === undefined) return this.node.src;

    this.node.src = v || '';
    return this;
  }

  /** Wire all text inputs. */
  static wire(conn, root?) {
    if (root === undefined) root = document;

    [].slice.call(root.getElementsByTagName('IMG'), 0)
      .filter(node => (<HTMLDatabenchElement>node).databenchUI === undefined)
      .filter(node => (<HTMLElement>node).dataset['signal'] !== undefined)
      .filter(node => UIElement.determineWireSignal(node) !== null)
      .forEach(node => {
        const img = new Image(node);
        console.log('Wiring image', node, `to signal ${img.wireSignal}.`);

        // handle events from backend
        conn.on(img.wireSignal, message => img.value(message));
      });
  }
}


/**
 * Wire all the UI elements to the backend. The action name is determined by
 * {@link module:ui~UIElement.determineActionName|UIElement.determineActionName()}
 * and the action message can be modified by overwriting
 * {@link module:ui~UIElement#actionFormat|UIElement.actionFormat()}. The signal
 * name is determined by
 * {@link module:ui~UIElement.determineWireSignal|UIElement.determineWireSignal()}.
 *
 * @param  {Connection} connection A Databench.Connection instance.
 * @return {Connection}            The same connection.
 */
export function wire(connection, root?) {
  StatusLog.wire(connection, root);
  Button.wire(connection, root);
  TextInput.wire(connection, root);
  Text.wire(connection, root);
  Slider.wire(connection, root);
  Image.wire(connection, root);
  Log.wire(connection, root);

  return connection;
}
