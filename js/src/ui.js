/** @module */

/** Abstract class for user interface elements. */
class UIElement {
  /**
   * Create a UI element.
   * @param  {HTMLElement} node An HTML element.
   */
  constructor(node) {
    this.node = node;
    this.node.databench_ui = this;

    this.action_name = UIElement.determine_action_name(node);
    this.action_format = value => value;

    this.wire_signal = { data: this.action_name };
  }

  /**
   * Determine the name of the action that should be associated with the node.
   * @param  {HTMLElement} node An HTML element.
   * @return {string}      Name of action or null.
   */
  static determine_action_name(node) {
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
export class Log extends UIElement {
  /**
   * Construct a log class.
   * @param  {HTMLElement} node          Primary node.
   * @param  {String} consoleFnName Name of console method to replace.
   * @param  {Number} limit         Maximum number of messages to show.
   * @param  {Number} length_limit  Maximum length of a message.
   */
  constructor(node, consoleFnName = 'log', limit = 20, length_limit = 250) {
    super(node);

    this.consoleFnName = consoleFnName;
    this.limit = limit;
    this.length_limit = length_limit;
    this._messages = [];

    // more sensible default for this case
    this.wire_signal = { log: null };

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
      .map(m => ((m.length > this.length_limit)
                 ? `${m.substr(0, this.length_limit)} ...`
                 : m))
      .join('\n');

    return this;
  }

  add(message, source = 'unknown') {
    const msg = typeof message === 'string' ? message : JSON.stringify(message);
    const padded_source = ' '.repeat(Math.max(0, 8 - source.length)) + source;
    this._messages.push([`${padded_source}: ${msg}`]);
    this.render();
    return this;
  }

  static wire(conn, id = 'log', source = 'backend', consoleFnName = 'log',
              limit = 20, length_limit = 250) {
    const node = document.getElementById(id);
    if (node == null) return this;

    console.log(`Wiring element id=${id}.`);
    const l = new Log(node, consoleFnName, limit, length_limit);
    conn.on(l.wire_signal, message => l.add(message, source));
    return this;
  }
}


/** Visual element for console.log(). */
export class StatusLog extends UIElement {
  constructor(node, formatter = StatusLog.default_alert) {
    super(node);

    this.formatter = formatter;
    this._messages = new Map();

    // to avoid confusion, void meaningless parent variable
    this.wire_signal = null;

    // bind methods
    this.render = this.render.bind(this);
    this.add = this.add.bind(this);
  }

  static default_alert(msg, count) {
    const count_format = count <= 1 ? '' : `<b>(${count})</b> `;
    return `<div class="alert alert-danger">${count_format}${msg}</div>`;
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

  static wire(conn, id = 'ws-alerts', formatter = StatusLog.default_alert) {
    const node = document.getElementById(id);
    if (node == null) return;

    console.log(`Wiring element id=${id}.`);
    const l = new StatusLog(node, formatter);
    conn.error_cb = l.add;
  }
}


/** A button. */
export class Button extends UIElement {
  constructor(node) {
    super(node);

    this.IDLE = 0;
    this.ACTIVE = 2;

    this.click_cb = (processID) => console.log(`click on ${this.node} with ${processID}`);
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
    this.click_cb(processID);
    return this;
  }

  state(s) {
    if (s !== this.IDLE && s !== this.ACTIVE) return this;

    this._state = s;
    this.render();
    return this;
  }

  static wire(conn) {
    Array.from(document.getElementsByTagName('BUTTON'))
      .filter(node => node.databench_ui === undefined)
      .forEach(node => {
        const b = new Button(node);
        console.log(`Wiring button ${node} to action ${b.action_name}.`);

        // set up click callback
        b.click_cb = (processID) => {
          // set up process callback
          conn.onProcess(processID, status => b.state(
            // map process status to state
            { start: b.ACTIVE, end: b.IDLE }[status]
          ));

          conn.emit(b.action_name, b.action_format({ __process_id: processID }));
        };
      });
  }
}


/** Data bound text elements. */
export class Text extends UIElement {
  constructor(node) {
    super(node);

    this.format_fn = value => value;

    // bind methods
    this.value = this.value.bind(this);
  }

  value(v) {
    // reading value
    if (v === undefined) return this.node.innerHTML;

    this.node.innerHTML = this.format_fn(v || '');
    return this;
  }

  static wire(conn) {
    [...Array.from(document.getElementsByTagName('SPAN')),
     ...Array.from(document.getElementsByTagName('P')),
     ...Array.from(document.getElementsByTagName('DIV')),
     ...Array.from(document.getElementsByTagName('I')),
     ...Array.from(document.getElementsByTagName('B'))]
      .filter(node => node.databench_ui === undefined)
      .filter(node => node.dataset.action !== undefined)
      .filter(node => UIElement.determine_action_name(node) !== null)
      .forEach(node => {
        const t = new Text(node);
        console.log(`Wiring text ${node} to action ${t.action_name}.`);

        // handle events from backend
        conn.on(t.wire_signal, message => t.value(message));
      });
  }
}

/** Make an input element of type text interactive. */
export class TextInput extends UIElement {
  /**
   * Create a TextInput UIElement.
   * @param {HTMLElement} node The node to connect.
   */
  constructor(node) {
    super(node);

    this.trigger_on_keyup = false;
    this.format_fn = value => value;
    this.change_cb = value => console.log(`change of ${this.node}: ${value}`);

    // bind methods
    this.change = this.change.bind(this);
    this.keyup = this.keyup.bind(this);
    this.value = this.value.bind(this);

    this.node.addEventListener('change', this.change, false);
    this.node.addEventListener('keyup', this.keyup, false);
  }

  change() {
    return this.change_cb(this.action_format(this.value()));
  }

  keyup() {
    if (this.trigger_on_keyup) this.change();
  }

  value(v) {
    // reading value
    if (v === undefined) return this.node.value;

    this.node.value = this.format_fn(v || '');
    return this;
  }

  static wire(conn) {
    Array.from(document.getElementsByTagName('INPUT'))
      .filter(node => node.databench_ui === undefined)
      .filter(node => node.getAttribute('type') === 'text')
      .forEach(node => {
        const t = new TextInput(node);
        console.log(`Wiring text input ${node} to action ${t.action_name}.`);

        // handle events from frontend
        t.change_cb = message => conn.emit(t.action_name, message);

        // handle events from backend
        conn.on(t.wire_signal, message => t.value(message));
      });
  }
}


/** A range slider. */
export class Slider extends UIElement {
  constructor(node, label_node) {
    super(node);

    this.label_node = label_node;
    this.label_html = label_node ? label_node.innerHTML : null;
    this.change_cb = value => console.log(`slider value change: ${value}`);
    this.value_to_slider = value => value;
    this.slider_to_value = s => s;
    this.format_fn = value => value;

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
    if (this.label_node) {
      this.label_node.innerHTML = `${this.label_html} ${this.format_fn(v)}`;
    }
    return this;
  }

  value(v) {
    // reading value
    if (v === undefined) {
      return this.slider_to_value(parseFloat(this.node.value));
    }

    const new_slider_value = this.value_to_slider(v);
    if (this.node.value === new_slider_value) return this;

    this.node.value = new_slider_value;
    this.render();
    return this;
  }

  change() {
    return this.change_cb(this.action_format(this.value()));
  }

  static preprocess_labels() {
    Array.from(document.getElementsByTagName('LABEL'))
      .filter(label => label.htmlFor)
      .forEach(label => {
        const node = document.getElementById(label.htmlFor);
        if (node) node.label = label;
      });
  }

  static wire(conn) {
    this.preprocess_labels();

    Array.from(document.getElementsByTagName('INPUT'))
      .filter(node => node.databench_ui === undefined)
      .filter(node => node.getAttribute('type') === 'range')
      .forEach(node => {
        const slider = new Slider(node, node.label);
        console.log(`Wiring slider ${node} to action ${slider.action_name}.`);

        // handle events from frontend
        slider.change_cb = message => conn.emit(slider.action_name, message);

        // handle events from backend
        conn.on(slider.wire_signal, message => slider.value(message));
      });
  }
}

/**
 * Wire all the UI elements to the backend.
 * @param  {Connection} connection A Databench.Connection instance.
 * @return {Connection}            The same connection.
 */
export function wire(connection) {
  StatusLog.wire(connection);
  Log.wire(connection);
  Button.wire(connection);
  TextInput.wire(connection);
  Text.wire(connection);
  Slider.wire(connection);
  return connection;
}
