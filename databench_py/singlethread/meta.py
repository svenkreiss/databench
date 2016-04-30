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
        import_name (str): Usually the file name ``__name__`` where this
            analysis is instantiated.
        description (str): Usually the ``__doc__`` string of the analysis.
        analysis (Analysis): Analysis class.

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

    def run_action(self, analysis, fn_name, message='__nomessagetoken__'):
        """Executes an action in the analysis with the given message.

        It also handles the start and stop signals in case an action_id
        is given.

        This method is exactly the same as in databench.Analysis.
        """

        # detect action_id
        action_id = None
        if isinstance(message, dict) and '__action_id' in message:
            action_id = message['__action_id']
            del message['__action_id']

        if action_id:
            analysis.emit('__action', {'id': action_id, 'status': 'start'})

        log.debug('kernel calling {}'.format(fn_name))
        fn = getattr(analysis, fn_name)
        log.debug('kernel done {}'.format(fn_name))

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

        if action_id:
            analysis.emit('__action', {'id': action_id, 'status': 'end'})

        if fn_name == 'on_disconnect':
            log.debug('kernel {} shutting down'.format(analysis.id_))
            self.zmq_publish.close()

            self.zmq_stream_sub.close()
            self.zmq_sub.close()
            self.zmq_sub_ctx.destroy()

    def event_loop(self):
        """Event loop."""
        zmq.eventloop.ioloop.IOLoop.current().start()

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

        if not hasattr(self.analysis,
                       'on_{}'.format(msg['signal'])):
            log.warning('Analysis does not contain on_{}()'
                        ''.format(msg['signal']))
            return

        # standard message
        fn_name = 'on_{}'.format(msg['signal'])
        log.debug('kernel processing {}'.format(fn_name))
        self.run_action(self.analysis, fn_name, msg['load'])

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
