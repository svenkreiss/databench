/** @module ui */


/** Abstract class for user interface elements. */
class UIElement {
  /**
   * Create a UI element.
   * @param  {HTMLElement} node An HTML element.
   */
  constructor(node) {
    this.node = node;
    this.node.databenchUI = this;

    this.actionName = UIElement.determineActionName(node);
    this.actionFormat = value => value;

    this.wireSignal = { data: this.actionName };
  }

  /**
   * Determine the name of the action that should be associated with the node.
   * @param  {HTMLElement} node An HTML element.
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
}

/** Log messages class. */
class Log extends UIElement {
  /**
   * Construct a log class.
   * @param  {HTMLElement} node     Primary node.
   * @param  {String} [consoleFnName='log'] Name of console method to replace.
   * @param  {Number} [limit=20]            Maximum number of messages to show.
   * @param  {Number} [lengthLimit=250]     Maximum length of a message.
   */
  constructor(node, consoleFnName = 'log', limit = 20, lengthLimit = 250) {
    super(node);

    this.consoleFnName = consoleFnName;
    this.limit = limit;
    this.lengthLimit = lengthLimit;
    this._messages = [];

    // more sensible default for this case
    this.wireSignal = { log: null };

    // bind methods
    this.render = this.render.bind(this);
    this.add = this.add.bind(this);

    // capture events from frontend
    const _consoleFnOriginal = console[consoleFnName];
    console[consoleFnName] = message => {
      this.add(message, 'frontend');
      _consoleFnOriginal.apply(console, [message]);
    };
  }

  render() {
    while (this._messages.length > this.limit) this._messages.shift();

    this.node.innerText = this._messages
      .map(m => m.join(''))
      .map(m => ((m.length > this.lengthLimit)
                 ? `${m.substr(0, this.lengthLimit)} ...`
                 : m))
      .join('\n');

    return this;
  }

  add(message, source = 'unknown') {
    const msg = typeof message === 'string' ? message : JSON.stringify(message);
    const paddedSource = ' '.repeat(Math.max(0, 8 - source.length)) + source;
    this._messages.push([`${paddedSource}: ${msg}`]);
    this.render();
    return this;
  }

  /** Wire all logs. */
  static wire(conn, id = 'log', source = 'backend', consoleFnName = 'log',
              limit = 20, lengthLimit = 250) {
    const node = document.getElementById(id);
    if (node == null) return this;

    console.log(`Wiring element id=${id}.`);
    const l = new Log(node, consoleFnName, limit, lengthLimit);
    conn.on(l.wireSignal, message => l.add(message, source));
    return this;
  }
}


/** Visual element for console.log(). */
class StatusLog extends UIElement {
  constructor(node, formatter = StatusLog.defaultAlert) {
    super(node);

    this.formatter = formatter;
    this._messages = new Map();

    // to avoid confusion, void meaningless parent variable
    this.wireSignal = null;

    // bind methods
    this.render = this.render.bind(this);
    this.add = this.add.bind(this);
  }

  static defaultAlert(msg, count) {
    const countFormat = count <= 1 ? '' : `<b>(${count})</b> `;
    return `<div class="alert alert-danger">${countFormat}${msg}</div>`;
  }

  render() {
    const formatted = [...this._messages].map(([m, c]) => this.formatter(m, c));
    this.node.innerHTML = formatted.join('\n');
    return this;
  }

  add(message) {
    if (message == null) {
      this._messages.clear();
      return this;
    }
    const msg = typeof message === 'string' ? message : JSON.stringify(message);

    if (this._messages.has(msg)) {
      this._messages.set(msg, this._messages.get(msg) + 1);
    } else {
      this._messages.set(msg, 1);
    }
    this.render();
    return this;
  }

  /** Wire all status logs. */
  static wire(conn, id = 'ws-alerts', formatter = StatusLog.defaultAlert) {
    const node = document.getElementById(id);
    if (node == null) return;

    console.log(`Wiring element id=${id}.`);
    const l = new StatusLog(node, formatter);
    conn.errorCB = l.add;
  }
}


/** A button. */
class Button extends UIElement {
  /**
   * Bind button.
   * @param  {HTMLElement} node DOM node to connect.
   */
  constructor(node) {
    super(node);

    this.IDLE = 0;
    this.ACTIVE = 2;

    this.clickCB = (processID) => console.log(`click on ${this.node} with ${processID}`);
    this._state = this.IDLE;

    // bind methods
    this.render = this.render.bind(this);
    this.click = this.click.bind(this);
    this.state = this.state.bind(this);

    this.node.addEventListener('click', this.click, false);
  }

  render() {
    switch (this._state) {
      case this.ACTIVE:
        this.node.classList.add('disabled');
        break;
      default:
        this.node.classList.remove('disabled');
    }
    return this;
  }

  click() {
    if (this._state !== this.IDLE) return this;

    const processID = Math.floor(Math.random() * 0x100000);
    this.clickCB(processID);
    return this;
  }

  state(s) {
    if (s !== this.IDLE && s !== this.ACTIVE) return this;

    this._state = s;
    this.render();
    return this;
  }

  /** Wire all buttons. */
  static wire(conn) {
    Array.from(document.getElementsByTagName('BUTTON'))
      .filter(node => node.databenchUI === undefined)
      .forEach(node => {
        const b = new Button(node);
        console.log(`Wiring button ${node} to action ${b.actionName}.`);

        // set up click callback
        b.clickCB = (processID) => {
          // set up process callback
          conn.onProcess(processID, status => b.state(
            // map process status to state
            { start: b.ACTIVE, end: b.IDLE }[status]
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
 * @extends {UIElement}
 */
class Text extends UIElement {
  constructor(node) {
    super(node);

    this.formatFn = value => value;

    // bind methods
    this.value = this.value.bind(this);
  }

  value(v) {
    // reading value
    if (v === undefined) return this.node.innerHTML;

    this.node.innerHTML = this.formatFn(v || '');
    return this;
  }

  /**
   * Wire all text.
   * @param  {Connection} conn Connection to use.
   * @static
   * @memberof ui.Text
   */
  static wire(conn) {
    [...Array.from(document.getElementsByTagName('SPAN')),
     ...Array.from(document.getElementsByTagName('P')),
     ...Array.from(document.getElementsByTagName('DIV')),
     ...Array.from(document.getElementsByTagName('I')),
     ...Array.from(document.getElementsByTagName('B'))]
      .filter(node => node.databenchUI === undefined)
      .filter(node => node.dataset.action !== undefined)
      .filter(node => UIElement.determineActionName(node) !== null)
      .forEach(node => {
        const t = new Text(node);
        console.log(`Wiring text ${node} to action ${t.actionName}.`);

        // handle events from backend
        conn.on(t.wireSignal, message => t.value(message));
      });
  }
}


/** Make an input element of type text interactive. */
class TextInput extends UIElement {
  /**
   * Create a TextInput UIElement.
   * @param {HTMLElement} node The node to connect.
   */
  constructor(node) {
    super(node);

    this._triggerOnKeyUp = false;
    this.formatFn = value => value;
    this.changeCB = value => console.log(`change of ${this.node}: ${value}`);

    // bind methods
    this.change = this.change.bind(this);
    this.triggerOnKeyUp = this.triggerOnKeyUp.bind(this);
    this.value = this.value.bind(this);

    this.node.addEventListener('change', this.change, false);
  }

  change() {
    return this.changeCB(this.actionFormat(this.value()));
  }

  triggerOnKeyUp(v) {
    if (v !== false && !this._triggerOnKeyUp) {
      this.node.addEventListener('keyup', this.change, false);
      this._triggerOnKeyUp = true;
    }

    if (v === false && this._triggerOnKeyUp) {
      this.node.removeEventListener('keyup', this.change, false);
      this._triggerOnKeyUp = false;
    }
  }

  value(v) {
    // reading value
    if (v === undefined) return this.node.value;

    this.node.value = this.formatFn(v || '');
    return this;
  }

  /** Wire all text inputs. */
  static wire(conn) {
    Array.from(document.getElementsByTagName('INPUT'))
      .filter(node => node.databenchUI === undefined)
      .filter(node => node.getAttribute('type') === 'text')
      .forEach(node => {
        const t = new TextInput(node);
        console.log(`Wiring text input ${node} to action ${t.actionName}.`);

        // handle events from frontend
        t.changeCB = message => conn.emit(t.actionName, message);

        // handle events from backend
        conn.on(t.wireSignal, message => t.value(message));
      });
  }
}


/** A range slider. */
class Slider extends UIElement {
  /**
   * Data bind a slider.
   * @param  {HTMLElement} node      DOM node to bind.
   * @param  {HTMLElement} labelNode DOM node label that corresponds to the slider.
   */
  constructor(node, labelNode) {
    super(node);

    this.labelNode = labelNode;
    this.labelHtml = labelNode ? labelNode.innerHTML : null;
    this.changeCB = value => console.log(`slider value change: ${value}`);
    this.valueToSlider = value => value;
    this.sliderToValue = s => s;
    this.formatFn = value => value;

    // bind methods
    this.render = this.render.bind(this);
    this.value = this.value.bind(this);
    this.change = this.change.bind(this);

    this.node.addEventListener('input', this.render, false);
    this.node.addEventListener('change', this.change, false);
    this.render();
  }

  render() {
    const v = this.value();
    if (this.labelNode) {
      this.labelNode.innerHTML = `${this.labelHtml} ${this.formatFn(v)}`;
    }
    return this;
  }

  value(v) {
    // reading value
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

  /** Preprocess labels before wiring. */
  static preprocessLabels() {
    Array.from(document.getElementsByTagName('LABEL'))
      .filter(label => label.htmlFor)
      .forEach(label => {
        const node = document.getElementById(label.htmlFor);
        if (node) node.label = label;
      });
  }

  /** Wire all sliders. */
  static wire(conn) {
    this.preprocessLabels();

    Array.from(document.getElementsByTagName('INPUT'))
      .filter(node => node.databenchUI === undefined)
      .filter(node => node.getAttribute('type') === 'range')
      .forEach(node => {
        const slider = new Slider(node, node.label);
        console.log(`Wiring slider ${node} to action ${slider.actionName}.`);

        // handle events from frontend
        slider.changeCB = message => conn.emit(slider.actionName, message);

        // handle events from backend
        conn.on(slider.wireSignal, message => slider.value(message));
      });
  }
}

/**
 * Wire all the UI elements to the backend.
 * @param  {Connection} connection A Databench.Connection instance.
 * @return {Connection}            The same connection.
 */
function wire(connection) {
  StatusLog.wire(connection);
  Log.wire(connection);
  Button.wire(connection);
  TextInput.wire(connection);
  Text.wire(connection);
  Slider.wire(connection);
  return connection;
}

export { StatusLog, Log, Button, TextInput, Text, Slider, wire };
