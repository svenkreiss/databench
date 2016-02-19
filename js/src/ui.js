
export function wire(conn) {
    Databench04.ui.StatusLog.wire(d);
    Databench04.ui.Log.wire(d);
    Databench04.ui.Button.wire(d);
    Databench04.ui.Slider.wire(d);
    return conn;
}


export class Log {
    constructor(node, limit=20, consoleFnName='log') {
        this.node = node;
        this.limit = limit;
        this.consoleFnName = consoleFnName;
        this._messages = [];

        // capture events from frontend
        let _consoleFnOriginal = console[consoleFnName];
        console[consoleFnName] = (message) => {
            this.add(message, 'frontend');
            _consoleFnOriginal.apply(console, [message]);
        }
    }

    render = () => {
        while(this._messages.length > this.limit) this._messages.shift();
        this.node.innerText = this._messages.map((m) => m.join('')).join('\n');
        return this;
    };

    add = (message, source='unknown') => {
        if (typeof message != "string") {
            message = JSON.stringify(message);
        }

        let padded_source = ' '.repeat(Math.max(0, 8 - source.length)) + source;
        this._messages.push([`${padded_source}: ${message}`]);
        this.render();
        return this;
    };

    static wire(conn, id='log', source='backend', limit=20, consoleFnName='log') {
        let node = document.getElementById(id);
        if (node == null) return;

        console.log(`Wiring element id=${id} to ${source}.`);
        let l = new Log(node, limit, consoleFnName);
        conn.on('log', (message) => l.add(message, source));
        return this;
    }
};


export class StatusLog {
    constructor(node, formatter=StatusLog.default_alert) {
        this.node = node;
        this.formatter = formatter;
        this._messages = new Map();
    }

    static default_alert(msg, c) {
        let c_format = c <= 1 ? '' : `<b>(${c})</b> `;
        return `<div class="alert alert-danger">${c_format}${msg}</div>`;
    }

    render = () => {
        let formatted = [...this._messages].map(([m, c]) => this.formatter(m, c));
        this.node.innerHTML = formatted.join('\n');
        return this;
    };

    add = (msg) => {
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
    };

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
        this.click_cb = (actionID) => console.log(`click on ${this.node} with ${actionID}`);
        this._state = this.IDLE;

        this.node.addEventListener('click', this.click, false);
    }

    render = () => {
        switch (this._state) {
            case this.ACTIVE:
                this.node.classList.add('active');
                break;
            default:
                this.node.classList.remove('active');
        }
        return this;
    };

    click = () => {
        if (this._state != this.IDLE) return;

        let actionID = Math.floor(Math.random() * 0x100000);
        this.click_cb(actionID);
        return this;
    };

    state = (s) => {
        if (s != this.IDLE && s != this.ACTIVE) return;

        this._state = s;
        this.render();
        return this;
    };

    static wire(conn) {
        let nodes = Array.from(document.getElementsByTagName('BUTTON'));
        for (let n of nodes) {
            let signalName = n.dataset.signal;
            if (!signalName) continue;

            console.log(`Wiring button ${n}.`);
            let b = new Button(n);

            // set up click callback
            b.click_cb = (actionID) => {
                // set up action callback
                conn.onAction(actionID, (status) => {
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
                message['__action_id'] = actionID;
                conn.emit(signalName, message);
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
        this.v_to_slider = (value) => value;
        this.slider_to_v = (s) => s;

        this.node.addEventListener('change', this.change, false);
        this.render();
    }

    render = () => {
        let v = this.value();
        if (this.label_node) {
            this.label_node.innerHTML = `${this.label_html} (${v})`;
        }
        return this;
    };

    value = (v) => {
        if (!v) {
            // reading value
            v = this.slider_to_v(parseFloat(this.node.value));
            return v;
        }

        // setting value
        this.node.value = this.v_to_slider(v);
        this.render();
        return this;
    };

    change = () => {
        this.change_cb(this.value());
        this.render();
    };

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

            console.log(`Wiring slider ${n}.`);
            let s = new Slider(n, n.label);

            s.change_cb = (value) => {
                // construct message
                let message = s.value();
                if (n.dataset.message) {
                    message = JSON.parse(n.dataset.message);
                    message.value = s.value();
                }

                // construct signal
                let signal = null;
                if (n.dataset.signal) {
                    signal = n.dataset.signal;
                } else if (n.dataset.instance) {
                    message = { [n.dataset.instance]: message };
                    signal = 'data';
                } else if (n.dataset.global) {
                    message = { [n.dataset.global]: message };
                    signal = 'global_data';
                } else if (n.getAttribute('name')) {
                    signal = n.getAttribute('name');
                }
                if (!signal) {
                    console.log(`Could not determine signal name for ${n}.`);
                    return;
                }

                conn.emit(signal, message);
            };
        }
    }
}
