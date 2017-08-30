/**
 * This is a basic set of UI elements to create analyses without having to add
 * frontend frameworks like Angular or React.
 *
 * @module ui
 */

import { Connection } from './connection';

export namespace ui {


export interface HTMLDatabenchElement extends HTMLElement {
  databenchUI: UIElement;
}

/**
 * Abstract class for user interface elements which provides general helpers
 * to determine the action name from an HTML tag and a way to modify the message
 * that is sent with actions of wired elements.
 *
 * The constructor adds the variables `actionName` and `wireSignal` using
 * [[UIElement.determineActionName]] and
 * [[UIElement.determineWireSignal]] respectively.
 * It also adds `this` UI element to the DOM node at `databenchUI`.
 */
export class UIElement {
  node: HTMLDatabenchElement;
  actionName?: string;
  wireSignal?: string | { [x: string]: string; };

  /**
   * @param node  An HTML element.
   */
  constructor(node: HTMLElement|HTMLDatabenchElement) {
    this.node = <HTMLDatabenchElement>node;
    this.node.databenchUI = this;

    this.actionName = UIElement.determineActionName(node);
    this.wireSignal = UIElement.determineWireSignal(node);
  }

  /**
   * Formats the payload of an action.
   * @param  value Original payload.
   * @return       Modified payload.
   */
  actionFormat(value: any): any {
    return value;
  }

  /**
   * Determine the name of the action that should be associated with the node.
   *
   * This can be forced to be `null` by adding a `data-skipwire=true` attribute
   * to the HTML tag. If that is not found, the action name is determined from
   * the tag's `data-action`, `name` or `id` attribute (in that order).
   *
   * @param  node A HTML element.
   * @return      Name of action or null.
   */
  static determineActionName(node: HTMLElement): string|undefined {
    if (node.dataset.skipwire === 'true' ||
      node.dataset.skipwire === 'TRUE' ||
      node.dataset.skipwire === '1') {
      return undefined;
    }

    const dataAction = node.dataset.action;
    if (dataAction) return dataAction;

    const attrName = node.getAttribute('name');
    if (attrName) return attrName;

    const attrId = node.getAttribute('id');
    if (attrId) return attrId;

    return undefined;
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
   * @param  node A HTML element.
   * @return      Name of a signal or null.
   */
  static determineWireSignal(node: HTMLElement): string | { [x: string]: string; } | undefined {
    if (node.dataset.skipwire === 'true' ||
      node.dataset.skipwire === 'TRUE' ||
      node.dataset.skipwire === '1') {
        return undefined;
    }

    const dataSignal = node.dataset.signal;
    if (dataSignal) {
      if (dataSignal.indexOf(':') >= 1) {
        const [key, value] = dataSignal.split(':', 2);
        return { [key]: value };
      }
      return dataSignal;
    }

    const dataAction = node.dataset.action;
    if (dataAction) return { data: dataAction };

    const attrName = node.getAttribute('name');
    if (attrName) return { data: attrName };

    const attrId = node.getAttribute('id');
    if (attrId) return { data: attrId };

    return undefined;
  }
}

/**
 * Shows all `console.log()` messages and `log` actions from backend.
 *
 * Usually wired to a `<pre id="log">` element.
 */
export class Log extends UIElement {
  limitNumber: number;
  limitLength: number;
  _messages: string[][];

  /**
   * @param  node            Primary node.
   * @param  limitNumber     Maximum number of messages to show.
   * @param  limitLength     Maximum length of a message.
   */
  constructor(node: HTMLElement,
              limitNumber: number = 20,
              limitLength: number = 250) {
    super(node);

    this.limitNumber = limitNumber;
    this.limitLength = limitLength;
    this._messages = [];
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

  add(message: any, source = 'unknown') {
    const msg = typeof message === 'string' ? message : JSON.stringify(message);
    const paddedSource = Array(Math.max(0, 8 - source.length)).join(' ') + source;
    this._messages.push([`${paddedSource}: ${msg}`]);
    this.render();
    return this;
  }

  /** Wire all logs. */
  static wire(conn: Connection,
              id: string = 'log',
              wireSignals: string[] = ['log', 'warn', 'error'],
              limitNumber: number = 20,
              limitLength: number = 250) {
    const node = document.getElementById(id);
    if (node == null) return;
    if (UIElement.determineActionName(node) == null) return;

    const log = new Log(node, limitNumber, limitLength);
    console.log(`Wiring ${wireSignals} to `, node);
    wireSignals.forEach(wireSignal => {
      conn.on(wireSignal, message => {
        log.add(message, `backend (${wireSignal})`);
      });
      conn.preEmit(wireSignal, message => {
        log.add(message, `frontend (${wireSignal})`);
        return message;
      });
    });
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
   * @param  node       HTML node.
   * @param  formatter  Formats a message and a count to a string.
   */
  constructor(node: HTMLElement,
              formatter: (message: string, count: number) => string = StatusLog.defaultAlert) {
    super(node);

    this.formatter = formatter;
    this._messages = {};
  }

  /**
   * The default formatter function
   * @param  message   A message.
   * @param  count     Count of the message.
   * @returns HTML formatted version of the inputs.
   */
  static defaultAlert(message: string, count: number): string {
    const countFormat = count <= 1 ? '' : `<b>(${count})</b> `;
    return `<div class="alert alert-danger">${countFormat}${message}</div>`;
  }

  render() {
    const formatted = Object.getOwnPropertyNames(this._messages)
      .map((m: string) => this.formatter(m, this._messages[m]));
    this.node.innerHTML = formatted.join('\n');
    return this;
  }

  add(message: any) {
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
  static wire(conn: Connection,
              id: string = 'databench-alerts',
              formatter: (message: string, count: number) => string = StatusLog.defaultAlert) {
    const node = document.getElementById(id);
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
   * @param node   DOM node to connect.
   */
  constructor(node: HTMLElement) {
    super(node);

    this._state = ButtonState.Idle;

    this.node.addEventListener('click', this.click.bind(this), false);
  }

  /**
   * Called on click events. When a button is wired, this function is overwritten
   * with the actual function that is triggered on click events.
   * @param  processID   a random id for the process that could be started
   */
  clickCB(processID: number) {
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

  state(s: ButtonState) {
    if (s !== ButtonState.Idle && s !== ButtonState.Active) return this;

    this._state = s;
    this.render();
    return this;
  }

  /** Wire all buttons. */
  static wire(conn: Connection, root?: Document|HTMLElement) {
    if (root === undefined) root = document;

    const elements: HTMLDatabenchElement[] = [].slice.call(root.getElementsByTagName('BUTTON'), 0);
    elements
      .filter(node => node.databenchUI === undefined)
      .filter(node => UIElement.determineActionName(node) !== undefined)
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

          if (!b.actionName) throw Error('Failed to determine action name');
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
 * Wired to `<span>`, `<p>`, `<div>`, `<i>` and `<b>` tags with a
 * `data-action` attribute specifying the action name.
 */
export class Text extends UIElement {
  /**
   * Format the value.
   * @param  value  Value as represented in the backend.
   * @return Formatted representation of the value.
   */
  formatFn(value: any): string {
    return value;
  }

  /** Reads the value. */
  get_value() {
    return this.node.innerHTML;
  }

  /** Reads the value. */
  set_value(v?: string) {
    this.node.innerHTML = this.formatFn(v || '');
    return this;
  }

  /**
   * Wire all text.
   * @param  {Connection} conn Connection to use.
   */
  static wire(conn: Connection, root?: Document|HTMLElement) {
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
      .filter(node => UIElement.determineActionName(node) !== undefined)
      .forEach(node => {
        const t = new Text(node);
        console.log('Wiring text', node, `to action ${t.actionName}.`);

        // handle events from backend
        if (!t.wireSignal) throw Error('Failed to determine action name');
        conn.on(t.wireSignal, message => t.set_value(message));
      });
  }
}


/** Make an `<input[type='text']>` with an action name interactive. */
export class TextInput extends UIElement {
  node: HTMLInputElement & HTMLDatabenchElement;
  _triggerOnKeyUp: boolean;

  /**
   * @param node  The node to connect.
   */
  constructor(node: HTMLElement) {
    super(node);

    this._triggerOnKeyUp = false;

    this.node.addEventListener('change', this.change.bind(this), false);
  }

  /**
   * Format the value.
   * @param  value  Value as represented in the backend.
   * @return Formatted representation of the value.
   */
  formatFn(value: any): string {
    return value;
  }

  /**
   * Callback that is triggered on frontend changes.
   * @param  value  A formatted action.
   */
  changeCB(value: any) {
    return console.log(`change of ${this.node}: ${value}`);
  }

  change() {
    return this.changeCB(this.actionFormat(this.get_value()));
  }

  /**
   * The default is `false`, which means that the callback is only triggered on
   * `change` events (i.e. pressing enter or unfocusing the element).
   * Setting this to true will trigger on every `keyup` event of this element.
   *
   * @param  v Whether to trigger on `keyup` events. Default is true.
   * @return self
   */
  triggerOnKeyUp(v: boolean): TextInput {
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
  get_value(): string {
    return this.node.value;
  }

  /** Set value */
  value(v: string): TextInput {
    this.node.value = this.formatFn(v || '');
    return this;
  }

  /** Wire all text inputs. */
  static wire(conn: Connection, root?: Document|HTMLElement) {
    if (root === undefined) root = document;

    const elements: HTMLDatabenchElement[] = [].slice.call(root.getElementsByTagName('INPUT'), 0);
    elements
      .filter(node => node.databenchUI === undefined)
      .filter(node => node.getAttribute('type') === 'text')
      .filter(node => UIElement.determineActionName(node) !== undefined)
      .forEach(node => {
        const t = new TextInput(node);
        console.log('Wiring text input', node, `to action ${t.actionName}.`);

        // handle events from frontend
        t.changeCB = message => {
          if (!t.actionName) throw Error('Failed to determine action name');
          conn.emit(t.actionName, message);
        };

        // handle events from backend
        if (!t.wireSignal) throw Error('Failed to determine action name');
        conn.on(t.wireSignal, message => t.value(message));
      });
  }
}


/**
 * Make all `<input[type='range']>` with an action name interactive.
 *
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
  labelNode: HTMLElement | undefined;
  labelHtml: string;

  /**
   * @param  node       DOM node to bind.
   * @param  labelNode  DOM node label that corresponds to the slider.
   */
  constructor(node: HTMLElement, labelNode?: HTMLElement) {
    super(node);

    this.labelNode = labelNode;
    this.labelHtml = labelNode ? labelNode.innerHTML : '';

    this.node.addEventListener('input', this.render.bind(this), false);
    this.node.addEventListener('change', this.change.bind(this), false);
    this.render();
  }

  /**
   * Callback with changes to the slider value.
   * @param  value   Value from a sliderToValue() transform.
   */
  changeCB(value: number) {
    return console.log(`slider value change: ${value}`);
  }

  /**
   * Transform a backend value to a slider value.
   * @param   value  Value as stored in backend.
   * @return  Value for the HTML range element.
   */
  valueToSlider(value: number): string {
    return value.toString();
  }

  /**
   * Transform a value from the HTML range element to a value that should be stored.
   * @param  s  Value from HTML range element.
   * @return Value to store.
   */
  sliderToValue(s: number): number {
    return s;
  }

  /**
   * How a value should be represented.
   * For example, this can add units or convert from radians to degrees.
   * @param  value  Input value as it is stored in the backend.
   * @return Representation of a value.
   */
  formatFn(value: number): string {
    return value.toString();
  }

  render() {
    const v = this.get_value();
    if (this.labelNode) {
      this.labelNode.innerHTML = `${this.labelHtml} ${this.formatFn(v)}`;
    }
    return this;
  }

  /** Reads the value. */
  get_value(): number {
    return this.sliderToValue(parseFloat(this.node.value));
  }

  /** Reads the value. */
  set_value(v: number) {
    const newSliderValue = this.valueToSlider(v);
    if (this.node.value === newSliderValue) return this;

    this.node.value = newSliderValue;
    this.render();
    return this;
  }

  change() {
    return this.changeCB(this.actionFormat(this.get_value()));
  }

  /** Find all labels for slider elements. */
  static labelsForSliders(root: Document|HTMLElement) {
    let map: { [inputname: string]: HTMLLabelElement } = {};

    const elements: HTMLLabelElement[] = [].slice.call(root.getElementsByTagName('LABEL'), 0);
    elements
      .filter(label => label.htmlFor)
      .forEach(label => { map[label.htmlFor] = label; });
    return map;
  }

  /** Wire all sliders. */
  static wire(conn: Connection, root?: Document|HTMLElement) {
    if (root === undefined) root = document;
    const lfs = this.labelsForSliders(root);

    const elements: HTMLDatabenchElement[] = [].slice.call(root.getElementsByTagName('INPUT'), 0);
    elements
      .filter(node => node.databenchUI === undefined)
      .filter(node => node.getAttribute('type') === 'range')
      .filter(node => UIElement.determineActionName(node) !== undefined)
      .forEach(node => {
        const slider = new Slider(node, lfs[node.id]);
        console.log('Wiring slider', node, `to action ${slider.actionName}.`);

        // handle events from frontend
        slider.changeCB = message => {
          if (!slider.actionName) throw Error('Failed to determine action name');
          conn.emit(slider.actionName, message);
        };

        // handle events from backend
        if (!slider.wireSignal) throw Error('Failed to determine action name');
        conn.on(slider.wireSignal, message => slider.set_value(message));
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
  value(v?: string) {
    if (v === undefined) return this.node.src;

    this.node.src = v || '';
    return this;
  }

  /** Wire all text inputs. */
  static wire(conn: Connection, root?: Document|HTMLElement) {
    if (root === undefined) root = document;

    const elements: HTMLDatabenchElement[] = [].slice.call(root.getElementsByTagName('IMG'), 0);
    elements
      .filter(node => node.databenchUI === undefined)
      .filter(node => node.dataset['signal'] !== undefined)
      .filter(node => UIElement.determineWireSignal(node) !== null)
      .forEach(node => {
        const img = new Image(node);
        console.log('Wiring image', node, `to signal ${img.wireSignal}.`);

        // handle events from backend
        if (!img.wireSignal) throw Error('Failed to determine action name');
        conn.on(img.wireSignal, message => img.value(message));
      });
  }
}


/**
 * Wire all the UI elements to the backend. The action name is determined by
 * [[UIElement.determineActionName]] and the action message can be modified
 * by overwriting [[UIElement.actionFormat]]. The signal name is determined by
 * [[UIElement.determineWireSignal]].
 *
 * @param  connection  A Databench.Connection instance.
 * @return The same connection.
 */
export function wire(connection: Connection, root?: Document|HTMLElement): Connection {
  StatusLog.wire(connection);
  Button.wire(connection, root);
  TextInput.wire(connection, root);
  Text.wire(connection, root);
  Slider.wire(connection, root);
  Image.wire(connection, root);
  Log.wire(connection);

  return connection;
}


}  // namespace ui
