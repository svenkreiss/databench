import json
import logging
import subprocess
import tornado.gen
import zmq
import zmq.eventloop.zmqstream
from .analysis import Analysis, Meta

log = logging.getLogger(__name__)


class AnalysisZMQ(Analysis):
    def __init__(self, id_):
        super(AnalysisZMQ, self).__init__(id_)
        self.zmq_handshake = False

    def on_connect(self, executable, zmq_publish):
        self.zmq_publish = zmq_publish

        # determine a port_subscribe
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        port_subscribe = socket.bind_to_random_port(
            'tcp://127.0.0.1',
            min_port=3000, max_port=9000,
        )
        socket.close()
        context.destroy()
        log.debug('determined: port_subscribe={}'.format(port_subscribe))

        # zmq subscription to listen for messages from backend
        log.debug('main listening on port: {}'.format(port_subscribe))
        self.zmq_sub_ctx = zmq.Context()
        self.zmq_sub = self.zmq_sub_ctx.socket(zmq.SUB)
        self.zmq_sub.setsockopt(zmq.SUBSCRIBE, b'')
        self.zmq_sub.bind('tcp://127.0.0.1:{}'.format(port_subscribe))

        self.zmq_stream_sub = zmq.eventloop.zmqstream.ZMQStream(
            self.zmq_sub,
            tornado.ioloop.IOLoop.current(),
        )
        self.zmq_stream_sub.on_recv(self.zmq_listener)

        # launch the language kernel process
        e_params = executable + [
            '--analysis-id={}'.format(self.id_),
            '--zmq-publish={}'.format(port_subscribe),
        ]
        log.debug('launching: {}'.format(e_params))
        self.kernel_process = subprocess.Popen(e_params, shell=False)
        log.debug('finished on_connect for {}'.format(self.id_))

    def on_disconnected(self):
        # In autoreload, this callback needs to be processed synchronously.
        log.debug('terminating kernel process {}'.format(self.id_))
        if self.kernel_process is not None:
            try:
                self.kernel_process.terminate()
            except subprocess.OSError:
                pass
        self.zmq_stream_sub.close()
        self.zmq_sub.close()
        self.zmq_sub_ctx.destroy()
        self.zmq_handshake = False

    def zmq_send(self, data):
        self.zmq_publish.send('{}|{}'.format(
            self.id_,
            json.dumps(data),
        ).encode('utf-8'))

    def zmq_listener(self, multipart):
        # log.debug('main received multipart: {}'.format(multipart))
        msg = json.loads((b''.join(multipart)).decode('utf-8'))

        # zmq handshake
        if '__zmq_handshake' in msg:
            self.zmq_handshake = True
            self.zmq_send({'__zmq_ack': None})
            return

        # check message is for this analysis
        if 'analysis_id' not in msg or \
           msg['analysis_id'] != self.id_:
            return

        # execute callback
        if 'frame' in msg and \
           'signal' in msg['frame'] and \
           'load' in msg['frame']:
            self.emit(msg['frame']['signal'], msg['frame']['load'])


class MetaZMQ(Meta):
    """A Meta class that pipes all messages to ZMQ and back.

    The entire ZMQ interface of Databench is defined here and in
    :class`AnalysisZMQ`.

    """

    def __init__(self, name, executable, zmq_publish):
        super(MetaZMQ, self).__init__(name, AnalysisZMQ)

        self.executable = executable
        self.zmq_publish = zmq_publish

    @tornado.gen.coroutine
    def run_process(self, analysis, action_name, message='__nomessagetoken__'):
        """Executes an process in the analysis with the given message.

        It also handles the start and stop signals in case a process_id
        is given.
        """

        if action_name == 'connect':
            analysis.on_connect(self.executable, self.zmq_publish)

        while not analysis.zmq_handshake:
            yield tornado.gen.sleep(0.1)

        log.debug('sending action {}'.format(action_name))
        analysis.zmq_send({
            'signal': action_name,
            'load': message,
        })

        if action_name == 'disconnected':
            # Give kernel time to process disconnected message.
            yield tornado.gen.sleep(0.1)
            analysis.on_disconnected()
