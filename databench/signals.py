"""Databench Signals.

Provides communication between frontend and backend via socket.io.
"""

from flask.ext.socketio import emit


class Signals(object):
    """Databench Signals.

    Args:
        namespace (str): The namespace seperates communications of different
            analyses. This is used as Socket.IOs namespace for this analysis.

    """


    def __init__(self, namespace):
        self.signal_cache = []
        self.socketio = None
        self.namespace = namespace


    def emit(self, signal, message):
        """Emit signal to frontend.

        Args:
            signal (str): Name of the signal to be emitted.
            message: Message to be sent.

        """

        emit(signal, message, namespace='/'+self.namespace)


    def on(self, signal):
        """This is a decorator. Use for functions that listen to signals
        from the frontend.

        Args:
            signal (str): The name of the signal to listen for.

        """

        def decorator(callback):
            if not self.socketio:
                self.signal_cache.append((signal, callback))
            else:
                self.socketio.on_message(signal, callback, namespace='/'+self.namespace)

        return decorator


    def _set_socket_io(self, socketio):
        """Sets socket.io and applies all cached callbacks."""

        self.socketio = socketio
        for sc in self.signal_cache:
            self.socketio.on_message(sc[0], sc[1], namespace='/'+self.namespace)
        self.signal_cache = []

