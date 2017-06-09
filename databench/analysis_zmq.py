import json
import logging
import subprocess
import tornado.gen
import zmq
import zmq.eventloop.zmqstream

from .analysis import Analysis

log = logging.getLogger(__name__)


class AnalysisZMQ(Analysis):
    def __init__(self):
        pass

    def init_databench(self, id_):
        super(AnalysisZMQ, self).init_databench(id_)
        self.zmq_handshake = False
        return self

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
