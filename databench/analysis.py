"""Analysis module for Databench."""

import os
import json
import time
import gevent
import logging
import zipstream
import subprocess
import geventwebsocket
import zmq.green as zmq
from flask import Blueprint, render_template, Response


class Analysis(object):
    """Databench's analysis class.

    This contains the analysis code. Every browser connection corresponds to
    and instance of this class.

    **Incoming messages** are captured by specifying a class method starting
    with ``on_`` followed by the signal name. To capture the frontend signal
    ``run`` that is emitted with the JavaScript code

    .. code-block:: js

        // on the JavaScript frontend
        databench.emit('run', {my_param: 'helloworld'});

    use

    .. code-block:: python

        # here in Python
        def on_run(self, my_param):

    here. The entries of a dictionary will be used as keyword arguments in the
    function call; as in this example. If the emitted message is an array,
    the entries will be used as positional arguments in the function call.
    If the message is neither of type ``list`` nor ``dict`` (for example a
    plain ``string`` or ``float``), the function will be called with that
    as its first parameter.

    **Outgoing messages** are sent using ``emit(signal_name, message)``.
    For example, use

    .. code-block:: python

        self.emit('result', {'msg': 'done'})

    to send the signal ``result`` with the message ``{'msg': 'done'}`` to
    the frontend.

    """

    def __init__(self):
        pass

    def set_emit_fn(self, emit_fn):
        """Sets what the emit function for this analysis will be."""
        self.emit = emit_fn

    """Events."""

    def onall(self, message_data):
        logging.debug('onall called.')

    def on_connect(self):
        logging.debug('on_connect called.')

    def on_disconnect(self):
        logging.debug('on_disconnect called.')


class Meta(object):
    """
    Args:
        name (str): Name of this analysis. If ``signals`` is not specified,
            this also becomes the namespace for the WebSocket connection and
            has to match the frontend's :js:class:`Databench` ``name``.
        import_name (str): Usually the file name ``__name__`` where this
            analysis is instantiated.
        description (str): Usually the ``__doc__`` string of the analysis.
        analysis_class (:class:`databench.Analysis`): Object
            that should be instantiated for every new websocket connection.

    For standard use cases, you don't have to modify this class. However,
    If you want to serve more than the ``index.html`` page, say a
    ``details.html`` page, you can derive from this class and add this
    to the constructor

    .. code-block:: python

        self.blueprint.add_url_rule('/details.html', 'render_details',
                                    self.render_details)

    and add a new method to the class

    .. code-block:: python

        def render_details(self):
            return render_template(
                self.name+'/details.html',
                analysis_description=self.description
            )

    and create the file ``details.html`` similar to ``index.html``.

    """

    all_instances = []

    def __init__(
            self,
            name,
            import_name,
            description,
            analysis_class,
    ):
        Meta.all_instances.append(self)
        self.show_in_index = True

        self.name = name
        self.import_name = import_name
        self.header = {'logo': '/static/logo.svg', 'title': 'Databench'}
        self.description = description
        self.analysis_class = analysis_class

        analyses_path = os.getcwd()+'/'+'analyses'
        if not os.path.exists(analyses_path):
            analyses_path = os.getcwd()+'/'+'databench/analyses_packaged'
        if not os.path.exists(analyses_path):
            logging.info('Folder for '+self.name+' not found.')
        self.analyses_path = analyses_path

        # detect whether thumbnail.png is present
        if os.path.isfile(analyses_path+'/'+self.name+'/thumbnail.png'):
            self.thumbnail = 'thumbnail.png'

        self.blueprint = Blueprint(
            name,
            import_name,
            template_folder=analyses_path,
            static_folder=analyses_path+'/'+self.name,
            static_url_path='/static',
        )
        self.blueprint.add_url_rule('/', 'render_template',
                                    self.render_template)
        self.blueprint.add_url_rule('/<templatename>', 'render_template',
                                    self.render_template)
        self.blueprint.add_url_rule('/'+name+'.zip', 'zip_analysis',
                                    self.zip_analysis, methods=['GET'])

        self.sockets = None

    def render_template(self, templatename='index.html'):
        """Renders the main analysis frontend template."""
        logging.debug('Rendering '+templatename)
        return render_template(
            self.name+'/'+templatename,
            header=self.header,
            analysis_name=self.name,
            analysis_description=self.description,
        )

    def zip_analysis(self):
        def generator():
            z = zipstream.ZipFile(mode='w',
                                  compression=zipstream.ZIP_DEFLATED)

            # find all analysis files
            folder = self.analyses_path+'/'+self.name
            for root, dirnames, filenames in os.walk(folder):
                invisible_dirs = [d for d in dirnames if d[0] == '.']
                for d in invisible_dirs:
                    dirnames.remove(d)
                for filename in filenames:
                    if filename[0] == '.':
                        continue
                    if filename[-4:] == '.pyc':
                        continue

                    # add the file to zipstream
                    fullname = os.path.join(root, filename)
                    arcname = fullname.replace(self.analyses_path+'/', '')
                    z.write(fullname, arcname=arcname)

            # add requirements.txt if present
            if os.path.isfile(self.analyses_path+'/requirements.txt'):
                z.write(self.analyses_path+'/requirements.txt')

            for chunk in z:
                yield chunk

        response = Response(generator(), mimetype='application/zip')
        response.headers['Content-Disposition'] = \
            'attachment; filename='+self.name+'.zip'
        return response

    def wire_sockets(self, sockets, url_prefix=''):
        self.sockets = sockets
        self.sockets.add_url_rule(url_prefix+'/ws', 'ws_serve', self.ws_serve)

    def instantiate_analysis_class(self):
        return self.analysis_class()

    @staticmethod
    def run_action(analysis, fn_name, message):
        """Executes an action in the analysis with the given message. It
        also handles the start and stop signals in case an action_id
        is given."""

        # detect action_id
        action_id = None
        if isinstance(message, dict) and '__action_id' in message:
            action_id = message['__action_id']
            del message['__action_id']

        if action_id:
            analysis.emit('__action', {'id': action_id, 'status': 'start'})

        fn = getattr(analysis, fn_name)

        # Check whether this is a list (positional arguments)
        # or a dictionary (keyword arguments).
        if isinstance(message, list):
            fn(*message)
        elif isinstance(message, dict):
            fn(**message)
        else:
            fn(message)

        if action_id:
            analysis.emit('__action', {'id': action_id, 'status': 'end'})

    def ws_serve(self, ws):
        """Handle a new websocket connection."""
        logging.debug('ws_serve()')

        def emit(signal, message):
            try:
                ws.send(json.dumps({'signal': signal, 'load': message}))
            except geventwebsocket.WebSocketError:
                logging.info('websocket closed. could not send: '+signal +
                             ' -- '+str(message))

        analysis_instance = self.instantiate_analysis_class()
        logging.debug("analysis instantiated")
        analysis_instance.set_emit_fn(emit)
        greenlets = []
        greenlets.append(gevent.Greenlet.spawn(
            analysis_instance.on_connect
        ))

        def process_message(message):
            if message is None:
                logging.debug('empty message received.')
                return

            message_data = json.loads(message)
            analysis_instance.onall(message_data)
            if 'signal' not in message_data or 'load' not in message_data:
                logging.info('message not processed: '+message)
                return

            fn_name = 'on_'+message_data['signal']
            if not hasattr(self.analysis_class, fn_name):
                logging.warning('frontend wants to call '+fn_name +
                                ' which is not in the Analysis class.')
                return

            logging.debug('calling '+fn_name)
            # every 'on_' is processed in a separate greenlet
            greenlets.append(gevent.Greenlet.spawn(
                Meta.run_action, analysis_instance,
                fn_name, message_data['load']
            ))

        while True:
            try:
                message = ws.receive()
                logging.debug('received message: '+str(message))
                process_message(message)
            except geventwebsocket.WebSocketError:
                break

        # disconnected
        logging.debug("disconnecting analysis instance")
        gevent.killall(greenlets)
        analysis_instance.on_disconnect()


class AnalysisZMQ(Analysis):

    def __init__(self, namespace, instance_id, zmq_publish):
        self.namespace = namespace
        self.instance_id = instance_id
        self.zmq_publish = zmq_publish

    def onall(self, message_data):
        msg = {
            'analysis': self.namespace,
            'instance_id': self.instance_id,
            'frame': message_data,
        }
        self.zmq_publish.send_json(msg)
        logging.debug('onall called with: '+str(msg))

    def on_connect(self):
        msg = {
            'analysis': self.namespace,
            'instance_id': self.instance_id,
            'frame': {'signal': 'connect', 'load': {}},
        }
        self.zmq_publish.send_json(msg)
        logging.debug('on_connect called')

    def on_disconnect(self):
        msg = {
            'analysis': self.namespace,
            'instance_id': self.instance_id,
            'frame': {'signal': 'disconnect', 'load': {}},
        }
        self.zmq_publish.send_json(msg)
        logging.debug('on_disconnect called')


class MetaZMQ(Meta):
    """A Meta class that pipes all messages to ZMQ and back.

    The entire ZMQ interface of Databench is defined here and in
    :class`AnalysisZMQ`.

    """

    def __init__(
            self,
            name,
            import_name,
            description,

            executable,
            zmq_publish,
            port_subscribe=None,
    ):
        Meta.__init__(self, name, import_name, description, AnalysisZMQ)

        self.zmq_publish = zmq_publish

        self.zmq_analysis_id = 0
        self.zmq_analyses = {}
        self.zmq_confirmed = False

        # check whether we have to determine port_subscribe ourselves first
        if port_subscribe is None:
            context = zmq.Context()
            socket = context.socket(zmq.PUB)
            port_subscribe = socket.bind_to_random_port(
                'tcp://127.0.0.1',
                min_port=3000, max_port=9000,
            )
            context.destroy()
            logging.debug('determined: port_subscribe='+str(port_subscribe))

        # zmq subscription to listen for messages from backend
        logging.debug('main listening on port: '+str(port_subscribe))
        self.zmq_sub = zmq.Context().socket(zmq.SUB)
        self.zmq_sub.connect('tcp://127.0.0.1:'+str(port_subscribe))
        self.zmq_sub.setsockopt(zmq.SUBSCRIBE, '')

        # @copy_current_request_context
        def zmq_listener():
            while True:
                msg = self.zmq_sub.recv_json()
                self.zmq_confirmed = True
                logging.debug('main ('+') received '
                              'msg: '+str(msg))

                if 'description' in msg:
                    self.description = msg['description']

                if 'instance_id' in msg and \
                   msg['instance_id'] in self.zmq_analyses:
                    analysis = self.zmq_analyses[msg['instance_id']]
                    del msg['instance_id']

                    if 'frame' in msg and \
                       'signal' in msg['frame'] and \
                       'load' in msg['frame']:
                        analysis.emit(msg['frame']['signal'],
                                      msg['frame']['load'])
                    else:
                        logging.debug('dont understand this message: ' +
                                      str(msg))
                else:
                    logging.debug('instance_id not in message or '
                                  'AnalysisZMQ with that id not found.')
        self.zmq_listener = gevent.Greenlet.spawn(zmq_listener)

        # launch the language kernel process
        logging.debug('launching: '+str(executable))
        self.kernel_process = subprocess.Popen(executable, shell=False)

        # init language kernel
        def sending_init():
            while not self.zmq_confirmed:
                logging.debug('init kernel '+self.name+' to publish on '
                              'port '+str(port_subscribe))
                self.zmq_publish.send_json({
                    'analysis': self.name,
                    'publish_on_port': port_subscribe,
                })
                time.sleep(0.1)
        gevent.Greenlet.spawn(sending_init)

    def instantiate_analysis_class(self):
        self.zmq_analysis_id += 1
        i = self.analysis_class(self.name,
                                self.zmq_analysis_id,
                                self.zmq_publish)
        self.zmq_analyses[self.zmq_analysis_id] = i
        return i
