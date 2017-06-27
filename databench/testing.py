from .app import App
from collections import defaultdict
import json
import tornado
from tornado.testing import AsyncHTTPTestCase, AsyncHTTPSTestCase
from tornado.testing import gen_test  # noqa


class Connection(object):
    """WebSocket client connection to backend.

    :param str url: WebSocket url.
    :param str analysis_id: An id.
    :param str request_args: Request args.

    The instance variables ``data`` and ``class_data`` are automatically
    updated.
    """
    def __init__(self, url, analysis_id=None, request_args=None):
        self.url = url
        self.analysis_id = analysis_id
        self.request_args = request_args

        self.ws = None
        self.on_process_callbacks = defaultdict(list)
        self.on_callbacks = defaultdict(list)

        # emulate behavior of automatically updating data and class_data
        self.data = {}
        self.class_data = {}
        self.on_callbacks['data'].append(
            lambda d: self.data.update(d))
        self.on_callbacks['class_data'].append(
            lambda d: self.class_data.update(d))

    @tornado.gen.coroutine
    def connect(self, compression_options=None):
        """Connect to backend and initialize.

        :rtype: tornado.concurrent.Future
        """
        self.ws = yield tornado.websocket.websocket_connect(
            tornado.httpclient.HTTPRequest(self.url, validate_cert=False),
            # io_loop=self.testcase.io_loop, callback=self.testcase.stop,
            compression_options=compression_options)

        yield self.ws.write_message(json.dumps({
            '__connect': self.analysis_id,
            '__request_args': self.request_args,
        }))
        r = yield self.read()
        self.analysis_id = r['load']['analysis_id']
        raise tornado.gen.Return(self)

    @tornado.gen.coroutine
    def close(self):
        """Close a websocket connection.

        :rtype: tornado.concurrent.Future
        """
        self.ws.close()
        yield tornado.gen.sleep(1.0)

    @tornado.gen.coroutine
    def emit(self, action, message='__nomessagetoken__'):
        """Emit an action with a message.

        :param action: name of an action
        :param message: payload for the action
        :rtype: tornado.concurrent.Future
        """
        out = {'signal': action}
        if message != '__nomessagetoken__':
            out['load'] = message
        yield self.ws.write_message(json.dumps(out))

    @tornado.gen.coroutine
    def read(self):
        """Read a message from the websocket connection.

        :rtype: tornado.concurrent.Future
        """
        response = yield self.ws.read_message()
        message = json.loads(response)

        # processes
        if 'signal' in message and message['signal'] == '__process':
            id_ = message['load']['id']
            status = message['load']['status']
            for cb in self.on_process_callbacks[id_]:
                cb(status)

        # normal message
        if 'signal' in message:
            for cb in self.on_callbacks[message['signal']]:
                if 'load' in message:
                    cb(message['load'])
                else:
                    cb()

        raise tornado.gen.Return(message)

    def on(self, signal, callback):
        """Register a callback for a signal."""
        self.on_callbacks[signal].append(callback)

    def on_process(self, process_id, callback):
        """Register a callback for a process."""
        self.on_process_callbacks[process_id].append(callback)


class AnalysisTestCase(AsyncHTTPTestCase):
    """Test scaffolding for an analysis.

    ``analyses_path`` is the import path for the analyses.
    ``gen_test`` is an alias for ``tornado.testing.gen_test``.


    Example:

    .. literalinclude:: ../tests/test_testing.py
        :language: python

    """

    analyses_path = None

    def get_app(self):
        return App(self.analyses_path).tornado_app()

    def connection(self, analysis_name, analysis_id=None, request_args=None):
        """Create a WebSocket connection to the backend.

        :rtype: Connection
        """
        url = 'ws://127.0.0.1:{}/{}/ws'.format(self.get_http_port(),
                                               analysis_name)
        return Connection(url, analysis_id, request_args)

    def connect(self, analysis_name, analysis_id=None, request_args=None):
        """Create a WebSocket connection to the backend and connect to it.

        :rtype: tornado.concurrent.Future
        """
        return self.connection(analysis_name, analysis_id,
                               request_args).connect()


class AnalysisTestCaseSSL(AsyncHTTPSTestCase):
    """Same as :class:`AnalysisTestCase` but with SSL."""

    analyses_path = None

    def get_app(self):
        return App(self.analyses_path).tornado_app()

    def connection(self, analysis_name, analysis_id=None, request_args=None):
        url = 'wss://127.0.0.1:{}/{}/ws'.format(self.get_http_port(),
                                                analysis_name)
        return Connection(url, analysis_id, request_args)

    def connect(self, analysis_name, analysis_id=None, request_args=None):
        return self.connection(analysis_name, analysis_id,
                               request_args).connect()
