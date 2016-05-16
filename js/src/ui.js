
export function wire(connection) {
    StatusLog.wire(connection);
    Log.wire(connection);
    Button.wire(connection);
    TextInput.wire(connection);
    Text.wire(connection);
    Slider.wire(connection);
    return connection;
}

class UIElement {
    constructor(node) {
        this.node = node;
        this.node.databench_ui = this;

        this.action_name = UIElement.determine_action_name(node);
        this.action_format = value => value;

        this.wire_signal = {data: this.action_name};
    }

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
        }

        return action;
    }
}

export class Log extends UIElement {
    constructor(node, consoleFnName='log', limit=20, length_limit=250) {
        super(node);

        this.consoleFnName = consoleFnName;
        this.limit = limit;
        this.length_limit = length_limit;
        this._messages = [];

        // more sensible default for this case
        this.wire_signal = {log: null};

        // bind methods
        this.render = this.render.bind(this);
        this.add = this.add.bind(this);

        // capture events from frontend
        let _consoleFnOriginal = console[consoleFnName];
        console[consoleFnName] = (message) => {
            this.add(message, 'frontend');
            _consoleFnOriginal.apply(console, [message]);
        }
    }

    render() {
        while(this._messages.length > this.limit) this._messages.shift();

        this.node.innerText = this._messages
            .map((m) => m.join(''))
            .map((m) => ((m.length > this.length_limit)
                         ? m.substr(0, this.length_limit)+'...'
                         : m))
            .join('\n');

        return this;
    }

    add(message, source='unknown') {
        if (typeof message != "string") {
            message = JSON.stringify(message);
        }

        let padded_source = ' '.repeat(Math.max(0, 8 - source.length)) + source;
        this._messages.push([`${padded_source}: ${message}`]);
        this.render();
        return this;
    }

    static wire(conn, id='log', source='backend', consoleFnName='log', limit=20, length_limit=250) {
        let node = document.getElementById(id);
        if (node == null) return;

        console.log(`Wiring element id=${id}.`);
        let l = new Log(node, consoleFnName, limit, length_limit);
        conn.on(l.wire_signal, message => l.add(message, source));
        return this;
    }
};


export class StatusLog extends UIElement {
    constructor(node, formatter=StatusLog.default_alert) {
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
        let count_format = count <= 1 ? '' : `<b>(${count})</b> `;
        return `<div class="alert alert-danger">${count_format}${msg}</div>`;
    }

    render() {
        let formatted = [...this._messages].map(([m, c]) => this.formatter(m, c));
        this.node.innerHTML = formatted.join('\n');
        return this;
    }

    add(msg) {
        if (msg == null) {
            this._messages.clear();
            return;
        }
        if (typeof msg != "string") {
            msg = JSON.stringify(msg);
        }

        if (this._messages.has(msg)) {
            this._messages.set(msg, this._messages.get(msg) + 1);
        } else {
            this._messages.set(msg, 1);
        }
        this.render();
        return this;
    }

    static wire(conn, id='ws-alerts', formatter=StatusLog.default_alert) {
        let node = document.getElementById(id);
        if (node == null) return;

        console.log(`Wiring element id=${id}.`);
        let l = new StatusLog(node, formatter);
        conn.error_cb = l.add;
    }
};


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
        if (this._state != this.IDLE) return this;

        let processID = Math.floor(Math.random() * 0x100000);
        this.click_cb(processID);
        return this;
    }

    state(s) {
        if (s != this.IDLE && s != this.ACTIVE) return this;

        this._state = s;
        this.render();
        return this;
    }

    static wire(conn) {
        Array.from(document.getElementsByTagName('BUTTON'))
            .filter(node => node.databench_ui === undefined)
            .map(node => {
                let b = new Button(node);
                console.log(`Wiring button ${node} to action ${b.action_name}.`);

                // set up click callback
                b.click_cb = (processID) => {
                    // set up process callback
                    conn.onProcess(processID, status => b.state(
                        // map process status to state
                        {start: b.ACTIVE, end: b.IDLE}[status]
                    ));

                    conn.emit(b.action_name,
                              b.action_format({__process_id: processID}));
                };
            });
    }
}


export class Text extends UIElement {
    constructor(node) {
        super(node);

        this.format_fn = value => value;

        // bind methods
        this.value = this.value.bind(this);
    }

    value(v) {
        this.node.innerHTML = this.format_fn(v);
        return this;
    }

    static wire(conn) {
        [...Array.from(document.getElementsByTagName('SPAN')),
         ...Array.from(document.getElementsByTagName('P')),
         ...Array.from(document.getElementsByTagName('DIV')),
         ...Array.from(document.getElementsByTagName('I')),
         ...Array.from(document.getElementsByTagName('B'))]
            .filter(node => node.databench_ui === undefined)
            .filter(node => UIElement.determine_action_name(node) !== null)
            .map(node => {
                let t = new Text(node);
                console.log(`Wiring text ${node} to action ${t.action_name}.`);

                // handle events from backend
                conn.on(t.wire_signal, message => t.value(message));
            });
    }
}


export class TextInput extends UIElement {
    constructor(node) {
        super(node);

        this.format_fn = value => value;
        this.change_cb = value => console.log(`change of ${this.node}: ${value}`);

        // bind methods
        this.change = this.change.bind(this);
        this.value = this.value.bind(this);

        this.node.addEventListener('change', this.change, false);
    }

    change() {
        return this.change_cb(this.action_format(this.value()));
    }

    value(v) {
        if (!v) {
            // reading value
            return this.node.value;
        }

        this.node.value = this.format_fn(v);
        return this;
    }

    static wire(conn) {
        Array.from(document.getElementsByTagName('INPUT'))
            .filter(node => node.databench_ui === undefined)
            .filter(node => node.getAttribute('type') == 'text')
            .map(node => {
                let t = new TextInput(node);
                console.log(`Wiring text input ${node} to action ${t.action_name}.`);

                // handle events from frontend
                t.change_cb = message => conn.emit(t.action_name, message);

                // handle events from backend
                conn.on(t.wire_signal, message => t.value(message));
            });
    }
}


export class Slider extends UIElement {
    constructor(node, label_node) {
        super(node);

        this.label_node = label_node;
        this.label_html = label_node ? label_node.innerHTML : null;
        this.change_cb = value => console.log(`slider value change: ${value}`);
        this._v_to_slider = value => value;
        this._slider_to_v = s => s;
        this._v_repr = v => v;

        // bind methods
        this.v_to_slider = this.v_to_slider.bind(this);
        this.slider_to_v = this.slider_to_v.bind(this);
        this.v_repr = this.v_repr.bind(this);
        this.render = this.render.bind(this);
        this.value = this.value.bind(this);
        this.change = this.change.bind(this);

        this.node.addEventListener('input', this.render, false);
        this.node.addEventListener('change', this.change, false);
        this.render();
    }

    v_to_slider(fn) {
        this._v_to_slider = fn;
        return this;
    }

    slider_to_v(fn) {
        this._slider_to_v = fn;
        return this;
    }

    v_repr(fn) {
        this._v_repr = fn;
        this.render();
        return this;
    }

    render() {
        let v = this.value();
        if (this.label_node) {
            this.label_node.innerHTML = `${this.label_html} ${this._v_repr(v)}`;
        }
        return this;
    }

    value(v) {
        if (!v) {
            // reading value
            return this._slider_to_v(parseFloat(this.node.value));
        }

        let new_slider_value = this._v_to_slider(v);
        if (this.node.value == new_slider_value) return this;

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
            .map(label => {
                let node = document.getElementsByName(label.htmlFor)[0];
                if (node) node.label = label;
            });
    }

    static wire(conn) {
        this.preprocess_labels();

        Array.from(document.getElementsByTagName('INPUT'))
            .filter(node => node.databench_ui === undefined)
            .filter(node => node.getAttribute('type') == 'range')
            .map(node => {
                let s = new Slider(node, node.label);
                console.log(`Wiring slider ${node} to action ${s.action_name}.`);

                // handle events from frontend
                s.change_cb = message => conn.emit(s.action_name, message);

                // handle events from backend
                conn.on(s.wire_signal, message => s.value(message));
            });
    }
}
