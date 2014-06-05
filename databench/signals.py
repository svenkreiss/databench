"""Databench Signals.

Provides communication between frontend and backend via socket.io.
"""

from flask.ext.socketio import emit


class Signals(object):
    """Databench Signals."""

    def __init__(self, namespace):
        self.signal_cache = []
        self.socketio = None
        self.namespace = namespace

    def on(self, signal):
        """This is a decorator with an argument without a wrapper."""

        def decorator(callback):
            if not self.socketio:
                self.signal_cache.append((signal, callback))
            else:
                self.socketio.on_message(signal, callback, namespace='/'+self.namespace)

        return decorator

    def set_socket_io(self, socketio):
        """Sets socket.io and applies all cached callbacks."""
        self.socketio = socketio
        for sc in self.signal_cache:
            self.socketio.on_message(sc[0], sc[1], namespace='/'+self.namespace)
        self.signal_cache = []

    def emit(self, signal, message):
        """Emit signal to frontend."""
        emit(signal, message, namespace='/'+self.namespace)
