"""Databench Signals.

Provides communication between frontend and backend via socket.io.
"""

import time
import logging
from flask.ext import socketio


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
        logging.info(
            'backend (namespace='+self.namespace+', signal='+signal + '): ' + (
                (str(message)[:60] + '...')
                if len(str(message)) > 65
                else str(message)
            )
        )

        socketio.emit(signal, message, namespace='/'+self.namespace)

        # Now need to be make sure this message gets send and is not blocked
        # by continuing execution of the main thread. This can be done with
        # the following sleep(0.0)
        time.sleep(0.0)

    def on(self, signal):
        """This is a decorator. Use for functions that listen to signals
        from the frontend. The function that is decorated should have a single
        argument which is the message (a string).

        Args:
            signal (str): The name of the signal to listen for.

        """

        def decorator(callback):
            """Inner decorator function."""
            if not self.socketio:
                self.signal_cache.append((signal, callback))
            else:
                self.socketio.on_message(
                    signal,
                    callback,
                    namespace='/'+self.namespace
                )

        return decorator

    def on_rpc(self, signal):
        """This is a decorator. Use for functions that listen to signals
        from the frontend. The "message" is expected to be a dictionary
        which this decorator decodes to keyword arguments.

        .. versionadded:: 0.2.9

        Args:
            signal (str): The name of the signal to listen for.

        """

        def decorator(callback):
            """Inner decorator function."""

            def decode_dictionary(message):
                """Decodes a message containing a dictionary into keyword
                arguments."""

                callback(**message)

            if not self.socketio:
                self.signal_cache.append((signal, decode_dictionary))
            else:
                self.socketio.on_message(
                    signal,
                    decode_dictionary,
                    namespace='/'+self.namespace
                )

        return decorator

    def set_socket_io(self, socketio):
        """Sets socket.io and applies all cached callbacks."""
        logging.debug('set_socket_io()')

        self.socketio = socketio
        for cached_signal in self.signal_cache:
            self.socketio.on_message(
                cached_signal[0], cached_signal[1],
                namespace='/'+self.namespace
            )
        self.signal_cache = []
