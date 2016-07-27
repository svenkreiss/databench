from .app import App
from collections import defaultdict
import json
import tornado
from tornado.testing import AsyncHTTPTestCase, AsyncHTTPSTestCase


class Connection(object):
    """WebSocket client connection to backend.

    :param str url: WebSocket url.
    :param str analysis_id: An id.
    :param str request_args: Request args.
    """
    def __init__(self, url, analysis_id=None, request_args=None):
        self.url = url
        self.analysis_id = analysis_id
        self.request_args = request_args

        self.ws = None
        self.on_process_callbacks = defaultdict(list)
        self.on_callbacks = defaultdict(list)

    @tornado.gen.coroutine
    def connect(self, compression_options=None):
        self.ws = yield tornado.websocket.websocket_connect(
            tornado.httpclient.HTTPRequest(self.url, validate_cert=False),
            # io_loop=self.io_loop,
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
        """Close a websocket connection and wait for the server side.

        If we don't wait here, there are sometimes leak warnings in the
        tests.
        """
        self.ws.close()
        yield tornado.gen.sleep(1.0)

    @tornado.gen.coroutine
    def emit(self, action, message='__nomessagetoken__'):
        """Emit an action with a message.

        :param action: name of an action
        :param message: payload for the action
        """
        if message == '__nomessagetoken__':
            yield self.ws.write_message(
                json.dumps({'signal': action})
            )
        else:
            yield self.ws.write_message(
                json.dumps({'signal': action, 'load': message})
            )

    @tornado.gen.coroutine
    def read(self):
        """Read a message from the websocket connection."""
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
        self.on_callbacks[signal].append(callback)

    def on_process(self, process_id, callback):
        self.on_process_callbacks[process_id].append(callback)


class AnalysisTestCase(AsyncHTTPTestCase):
    """Test scaffolding for an analysis.

    ``analyses_path`` is the import path for the analyses.

    Similar to tornado websocket unit tests:
    see https://github.com/tornadoweb/tornado/blob/master/tornado/\
test/websocket_test.py
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


class AnalysisTestCaseSSL(AsyncHTTPSTestCase):
    """Test scaffolding for an analysis with SSL.

    ``analyses_path`` is the import path for the analyses.

    Similar to tornado websocket unit tests:
    see https://github.com/tornadoweb/tornado/blob/master/tornado/\
test/websocket_test.py
    """

    analyses_path = None

    def get_app(self):
        return App(self.analyses_path).tornado_app()

    def connection(self, analysis_name, analysis_id=None, request_args=None):
        """Create a WebSocket connection to the backend.

        :rtype: Connection
        """
        url = 'wss://127.0.0.1:{}/{}/ws'.format(self.get_http_port(),
                                                analysis_name)
        return Connection(url, analysis_id, request_args)
