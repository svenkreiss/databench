import zmq
import json
import time
import logging
import subprocess
import tornado.gen
import zmq.eventloop.zmqstream
from .analysis import Analysis, Meta

log = logging.getLogger(__name__)


class AnalysisZMQ(Analysis):
    def __init__(self, id_):
        super(AnalysisZMQ, self).__init__(id_)

    def on_connect(self, executable, zmq_publish, meta_info_cb):
        self.zmq_publish = zmq_publish
        self.meta_info_cb = meta_info_cb

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

        self.zmq_stream_sub = zmq.eventloop.zmqstream.ZMQStream(self.zmq_sub)
        self.zmq_stream_sub.on_recv(self.zmq_listener)

        # launch the language kernel process
        e_params = executable + [
            '--analysis-id={}'.format(self.id_),
            '--zmq-publish={}'.format(port_subscribe),
        ]
        log.debug('launching: {}'.format(e_params))
        self.kernel_process = subprocess.Popen(e_params, shell=False)
        time.sleep(1)  # give the external process time to start and subscribe

    @tornado.gen.coroutine
    def on_disconnect(self):
        # give kernel time to process disconnect message
        yield tornado.gen.sleep(1.0)

        log.debug('terminating kernel process {}'.format(self.id_))
        if self.kernel_process is not None:
            try:
                self.kernel_process.terminate()
            except subprocess.OSError:
                pass
        self.zmq_stream_sub.close()
        self.zmq_sub.close()
        self.zmq_sub_ctx.destroy()

    def zmq_listener(self, multipart):
        # log.debug('main received multipart: {}'.format(multipart))
        msg = json.loads((b''.join(multipart)).decode('utf-8'))

        # meta info
        if '__meta_attr' in msg:
            self.meta_info_cb(msg['__meta_attr'])

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

    def __init__(
            self,
            name,
            description,

            executable,
            zmq_publish,
            port_subscribe=None,
    ):
        super(MetaZMQ, self).__init__(name, description, AnalysisZMQ)

        self.executable = executable
        self.zmq_publish = zmq_publish

    def info(self, kv):
        for attr, value in kv.items():
            setattr(self, attr, value)

    def run_action(self, analysis, fn_name, message='__nomessagetoken__'):
        """Executes an action in the analysis with the given message. It
        also handles the start and stop signals in case an action_id
        is given."""

        if fn_name == 'on_connect':
            analysis.on_connect(self.executable, self.zmq_publish, self.info)

        log.debug('calling {}'.format(fn_name))
        signal_name = fn_name[3:] if fn_name.startswith('on_') else fn_name
        self.zmq_publish.send('{}|{}'.format(
            analysis.id_,
            json.dumps({'signal': signal_name, 'load': message}),
        ).encode('utf-8'))

        if fn_name == 'on_disconnect':
            analysis.on_disconnect()
