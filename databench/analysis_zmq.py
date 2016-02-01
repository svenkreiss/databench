import zmq
import json
import logging
import subprocess
import tornado.gen
import zmq.eventloop.zmqstream
from .analysis import Analysis, Meta

log = logging.getLogger(__name__)


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
        log.debug('onall called with: {}'.format(msg))

    def on_connect(self, request_args=None):
        msg = {
            'analysis': self.namespace,
            'instance_id': self.instance_id,
            'frame': {
                'signal': 'connect',
                'load': {
                    'request_args': request_args,
                }
            },
        }
        self.zmq_publish.send_json(msg)
        log.debug('on_connect called')

    def on_disconnect(self):
        msg = {
            'analysis': self.namespace,
            'instance_id': self.instance_id,
            'frame': {'signal': 'disconnect', 'load': {}},
        }
        self.zmq_publish.send_json(msg)
        log.debug('on_disconnect called')


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
            log.debug('determined: port_subscribe='+str(port_subscribe))

        # zmq subscription to listen for messages from backend
        log.debug('main listening on port: '+str(port_subscribe))
        self.zmq_sub = zmq.Context().socket(zmq.SUB)
        self.zmq_sub.setsockopt(zmq.SUBSCRIBE, b'')
        self.zmq_sub.connect('tcp://127.0.0.1:'+str(port_subscribe))

        self.zmq_stream_sub = zmq.eventloop.zmqstream.ZMQStream(self.zmq_sub)
        self.zmq_stream_sub.on_recv(self.zmq_listener)

        # launch the language kernel process
        log.debug('launching: '+str(executable))
        self.kernel_process = subprocess.Popen(executable, shell=False)
        self.init_kernel(port_subscribe)

    @tornado.gen.coroutine
    def init_kernel(self, port_subscribe):
        while not self.zmq_confirmed:
            log.debug('init kernel {} to publish on port {}'
                      ''.format(self.name, port_subscribe))
            try:
                self.zmq_publish.send_json({
                    'analysis': self.name,
                    'publish_on_port': port_subscribe,
                })
            except zmq.error.ZMQError:
                pass
            yield tornado.gen.sleep(0.1)

    def zmq_listener(self, multipart):
        self.zmq_confirmed = True
        log.debug('main received multipart: {}'.format(multipart))
        msg = json.loads((b''.join(multipart)).decode('utf-8'))

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
                log.debug('dont understand this message: {}'.format(msg))
        else:
            log.debug('instance_id not in message or '
                      'AnalysisZMQ with that id not found.')

    def instantiate_analysis_class(self):
        self.zmq_analysis_id += 1
        i = self.analysis_class(self.name,
                                self.zmq_analysis_id,
                                self.zmq_publish)
        self.zmq_analyses[self.zmq_analysis_id] = i
        return i
