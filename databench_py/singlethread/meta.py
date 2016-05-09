"""Meta class for Databench Python kernel."""

import json
import logging
import sys
import zmq

log = logging.getLogger(__name__)


class Meta(object):
    """Class providing Meta information about analyses.

    For Python kernels.

    Args:
        name (str): Name of this analysis.
        analysis_class (Analysis): Analysis class.

    """

    def __init__(self, name, analysis_class):
        self.name = name
        analysis_id, zmq_port_subscribe, zmq_port_publish = None, None, None
        for cl in sys.argv:
            if cl.startswith('--analysis-id'):
                analysis_id = cl.partition('=')[2]
            if cl.startswith('--zmq-subscribe'):
                zmq_port_subscribe = cl.partition('=')[2]
            if cl.startswith('--zmq-publish'):
                zmq_port_publish = cl.partition('=')[2]

        log.info('Analysis id: {}, port sub: {}, port pub: {}'.format(
                 analysis_id, zmq_port_subscribe, zmq_port_publish))

        self.analysis = analysis_class(analysis_id)

        def emit(signal, message):
            self.emit(signal, message, analysis_id)
        self.analysis.set_emit_fn(emit)

        self._init_zmq(zmq_port_publish, zmq_port_subscribe)
        log.info('Language kernel for {} initialized with '
                 'analysis id {}.'.format(self.name, self.analysis.id_))

    def _init_zmq(self, port_publish, port_subscribe):
        """Initialize zmq messaging.

        Listen on sub_port. This port might at
        some point receive the message to start publishing on a certain
        port, but until then, no publishing.
        """

        log.debug('kernel {} publishing on port {}'
                  ''.format(self.analysis.id_, port_publish))
        self.zmq_publish = zmq.Context().socket(zmq.PUB)
        self.zmq_publish.connect('tcp://127.0.0.1:{}'.format(port_publish))

        log.debug('kernel {} subscribed on port {}'
                  ''.format(self.analysis.id_, port_subscribe))
        self.zmq_sub_ctx = zmq.Context()
        self.zmq_sub = self.zmq_sub_ctx.socket(zmq.SUB)
        self.zmq_sub.setsockopt(zmq.SUBSCRIBE,
                                self.analysis.id_.encode('utf-8'))
        self.zmq_sub.connect('tcp://127.0.0.1:{}'.format(port_subscribe))

        self.zmq_stream_sub = zmq.eventloop.zmqstream.ZMQStream(self.zmq_sub)
        self.zmq_stream_sub.on_recv(self.zmq_listener)

        # send zmq handshakes until a zmq ack is received
        self.zmq_ack = False
        self.send_handshake()

    def send_handshake(self):
        if self.zmq_ack:
            return

        log.debug('kernel {} send handshake'.format(self.analysis.id_))
        try:
            self.zmq_publish.send_json({
                '__zmq_handshake': None,
            })
        except zmq.error.ZMQError:
            # socket was closed (maybe main databench process terminated)
            return

        # check again in a bit
        zmq.eventloop.ioloop.IOLoop.current().call_later(
            0.5,
            self.send_handshake
        )

    def run_process(self, analysis, action_name, message='__nomessagetoken__'):
        """Executes an process in the analysis with the given message.

        It also handles the start and stop signals in case an process_id
        is given.

        This method is exactly the same as in databench.Analysis.
        """

        # detect process_id
        process_id = None
        if isinstance(message, dict) and '__process_id' in message:
            process_id = message['__process_id']
            del message['__process_id']

        if process_id:
            analysis.emit('__process', {'id': process_id, 'status': 'start'})

        fn_name = 'on_{}'.format(action_name)
        log.debug('kernel calling {}'.format(fn_name))
        fn = getattr(analysis, fn_name)
        # Check whether this is a list (positional arguments)
        # or a dictionary (keyword arguments).
        if isinstance(message, list):
            fn(*message)
        elif isinstance(message, dict):
            fn(**message)
        elif message == '__nomessagetoken__':
            fn()
        else:
            fn(message)
        log.debug('kernel done {}'.format(fn_name))

        if process_id:
            analysis.emit('__process', {'id': process_id, 'status': 'end'})

        if action_name == 'disconnected':
            log.debug('kernel {} shutting down'.format(analysis.id_))
            self.zmq_publish.close()

            self.zmq_stream_sub.close()
            self.zmq_sub.close()
            self.zmq_sub_ctx.destroy()

    def event_loop(self):
        """Event loop."""
        try:
            zmq.eventloop.ioloop.IOLoop.current().start()
        except KeyboardInterrupt:
            zmq.eventloop.ioloop.IOLoop.current().stop()

    def zmq_listener(self, multipart):
        msg = (b''.join(multipart)).decode('utf-8')
        log.debug('kernel msg: {}'.format(msg))
        msg = json.loads(msg.partition('|')[2])

        if '__zmq_ack' in msg:
            log.debug('kernel {} received zmq_ack'.format(self.analysis.id_))
            self.zmq_ack = True
            return

        if 'signal' not in msg or 'load' not in msg:
            return

        # standard message
        action_name = msg['signal']
        log.debug('kernel processing {}'.format(action_name))
        self.run_process(self.analysis, action_name, msg['load'])

    def emit(self, signal, message, analysis_id):
        """Emit signal to main.

        Args:
            signal: Name of the signal to be emitted.
            message: Message to be sent.
            analysis_id: Identifies the instance of this analysis.

        """

        log.debug('kernel {} zmq send ({}): {}'
                  ''.format(analysis_id, signal, message))
        self.zmq_publish.send_json({
            'analysis_id': analysis_id,
            'frame': {'signal': signal, 'load': message},
        })
