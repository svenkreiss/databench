
export function wire(conn) {
    StatusLog.wire(d);
    Log.wire(d);
    Button.wire(d);
    Slider.wire(d);
    return conn;
}


export class Log {
    constructor(node, consoleFnName='log', limit=20, length_limit=250) {
        this.node = node;
        this.consoleFnName = consoleFnName;
        this.limit = limit;
        this.length_limit = length_limit;
        this._messages = [];

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

        console.log(`Wiring element id=${id} to ${source}.`);
        let l = new Log(node, consoleFnName, limit, length_limit);
        conn.on('log', (message) => l.add(message, source));
        return this;
    }
};


export class StatusLog {
    constructor(node, formatter=StatusLog.default_alert) {
        this.node = node;
        this.formatter = formatter;
        this._messages = new Map();

        // bind methods
        this.render = this.render.bind(this);
        this.add = this.add.bind(this);
    }

    static default_alert(msg, c) {
        let c_format = c <= 1 ? '' : `<b>(${c})</b> `;
        return `<div class="alert alert-danger">${c_format}${msg}</div>`;
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


export class Button {
    constructor(node) {
        this.IDLE = 0;
        this.ACTIVE = 2;

        this.node = node;
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
        if (this._state != this.IDLE) return;

        let processID = Math.floor(Math.random() * 0x100000);
        this.click_cb(processID);
        return this;
    }

    state(s) {
        if (s != this.IDLE && s != this.ACTIVE) return;

        this._state = s;
        this.render();
        return this;
    }

    static wire(conn) {
        let nodes = Array.from(document.getElementsByTagName('BUTTON'));
        for (let n of nodes) {
            let signal = n.dataset.signal;
            if (!signal) continue;

            console.log(`Wiring button ${n} to signal ${signal}.`);
            let b = new Button(n);

            // set up click callback
            b.click_cb = (processID) => {
                // set up action callback
                conn.onProcess(processID, (status) => {
                    switch (status) {
                        case 'start':
                            b.state(b.ACTIVE);
                            break;
                        case 'end':
                            b.state(b.IDLE);
                            break;
                        default:
                            console.log('error');
                    }
                });

                let message = {};
                if (n.dataset.message) message = JSON.parse(n.dataset.message);
                message['__process_id'] = processID;
                conn.emit(signal, message);
            };
        }
    }
}


export class Slider {
    constructor(node, label_node) {
        this.node = node;
        this.label_node = label_node;
        this.label_html = label_node ? label_node.innerHTML : null;
        this.change_cb = (value) => console.log(`slider value ${value}`);
        this._v_to_slider = (value) => value;
        this._slider_to_v = (s) => s;
        this._v_repr = (v) => v;

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
            v = this._slider_to_v(parseFloat(this.node.value));
            return v;
        }

        // setting value
        this.node.value = this._v_to_slider(v);
        this.render();
        return this;
    }

    change() {
        this.change_cb(this.value());
    }

    static wire(conn) {
        // preprocess all labels on the page
        let labels = Array.from(document.getElementsByTagName('LABEL'));
        for (let l of labels) {
            if (l.htmlFor) {
                let n = document.getElementsByName(l.htmlFor)[0];
                if (n) n.label = l;
            }
        }

        let nodes = Array.from(document.getElementsByTagName('INPUT'));
        for (let n of nodes) {
            if (n.getAttribute('type') != 'range') continue;

            // construct signal
            let signal = null;
            if (n.dataset.signal) {
                signal = n.dataset.signal;
            } else if (n.dataset.instance) {
                signal = 'data';
            } else if (n.dataset.global) {
                signal = 'global_data';
            } else if (n.getAttribute('name')) {
                signal = n.getAttribute('name');
            }
            if (!signal) {
                console.log(`Could not determine signal name for ${n}.`);
                return;
            }

            console.log(`Wiring slider ${n} to signal ${signal}.`);
            let s = new Slider(n, n.label);
            n.databench_ui = s;

            // handle events from frontend
            s.change_cb = (value) => {
                // construct message
                let message = s.value();
                if (n.dataset.message) {
                    message = JSON.parse(n.dataset.message);
                    message.value = s.value();
                }

                // process message in case signal bound to data or global_data
                if (signal == 'data') {
                    message = { [n.dataset.instance]: message };
                } else if (signal == 'global_data') {
                    message = { [n.dataset.global]: message };
                }

                conn.emit(signal, message);
            };

            // handle events from backend
            if (signal == 'data') {
                conn.on('data', (message) => {
                    if (n.dataset.instance in message) {
                        s.value(message[n.dataset.instance]);
                    }
                });
            } else if (signal == 'global_data') {
                conn.on('global_data', (message) => {
                    if (n.dataset.global in message) {
                        s.value(message[n.dataset.global]);
                    }
                });
            } else {
                conn.on(signal, (message) => s.value(message));
            }
        }
    }
}
