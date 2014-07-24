"""Analysis module for Databench Python kernel."""

import zmq
import time
import inspect
import logging


class Analysis(object):
    """Databench's analysis class.

    For Python kernels.

    Args:
        name (str): Name of this analysis. If ``signals`` is not specified,
            this also becomes the namespace for the Socket.IO connection and
            has to match the frontend's :js:class:`Databench` ``name``.
        description (str): Usually the ``__doc__`` string of the analysis.

    """

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

        self._init_zmq()

    def _init_zmq(self, sub_port=8041):
        """Initialize zmq messaging. Listen on sub_port. This port might at
        some point receive the message to start publishing on a certain
        port, but until then, no publishing."""

        self.zmq_socket_pub = None

        self.zmq_socket_sub = zmq.Context().socket(zmq.SUB)
        self.zmq_socket_sub.connect('tcp://127.0.0.1:'+str(sub_port))
        self.zmq_socket_sub.setsockopt(zmq.SUBSCRIBE, '')

    def _process_json(self, json):
        logging.debug('kernel received '+str(json))

        if 'publish_on_port' in json:
            if self.zmq_socket_pub:
                return
            port = json['publish_on_port']
            self.zmq_socket_pub = zmq.Context().socket(zmq.PUB)
            self.zmq_socket_pub.bind('tcp://127.0.0.1:'+str(port))
            logging.debug('kernel publishing on: ' +
                          'tcp://127.0.0.1:'+str(port))

            # wait for slow tcp bind
            time.sleep(0.5)

            logging.debug('kernel sending its events it listens to')
            listeners = [name[3:] for name, fn in inspect.getmembers(self)
                         if name.startswith('on_')]
            self.zmq_socket_pub.send_json({
                '__databench_namespace': self.name,
                'action': 'listeners_list',
                'listeners': listeners,
            })

        if 'action' in json:
            if json['action'] == 'event':
                logging.debug(json)
                if hasattr(self, 'on_'+json['event']):
                    getattr(self, 'on_'+json['event'])(
                        *json['event_message']
                    )

    def event_loop(self):
        """Event loop."""
        while True:
            msg = self.zmq_socket_sub.recv_json()
            logging.debug('kernel msg: '+str(msg))
            if '__databench_namespace' in msg and \
               msg['__databench_namespace'] == self.name:
                del msg['__databench_namespace']
                self._process_json(msg)

    def emit(self, signal, message):
        """Emit signal to frontend.

        Args:
            signal (str): Name of the signal to be emitted.
            message: Message to be sent.

        """
        logging.info(
            'backend (namespace='+self.name+', signal='+signal + '): ' + (
                (str(message)[:60] + '...')
                if len(str(message)) > 65
                else str(message)
            )
        )

        if self.zmq_socket_pub:
            self.zmq_socket_pub.send_json({
                '__databench_namespace': self.name,
                'action': 'emit',
                'signal': signal,
                'message': message,
            })
        else:
            logging.debug('zmq_socket_pub not defined yet.')

    """Events."""

    def on_connect(self):
        logging.debug('on_connect called.')
