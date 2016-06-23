from .app import App
import json
import tornado
from tornado.testing import AsyncHTTPTestCase, AsyncHTTPSTestCase


class TestConnection(object):
    def __init__(self):
        self.ws = None

    @tornado.gen.coroutine
    def connect(self, url, compression_options=None):
        self.ws = yield tornado.websocket.websocket_connect(
            tornado.httpclient.HTTPRequest(url, validate_cert=False),
            # io_loop=self.io_loop,
            compression_options=compression_options)

        yield self.ws.write_message('{"__connect": null}')
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
        raise tornado.gen.Return(json.loads(response))


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

    @tornado.gen.coroutine
    def ws_connect(self, analysis, compression_options=None):
        """Open a WebSocket connection to an analysis.

        Runs the handshake and sets ``connection.analysis_id``.

        :param analysis: name of an analysis
        """

        url = 'ws://127.0.0.1:{}/{}/ws'.format(self.get_http_port(), analysis)
        connection = yield TestConnection().connect(url, compression_options)

        self.assertEqual(len(connection.analysis_id), 8)
        raise tornado.gen.Return(connection)


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

    @tornado.gen.coroutine
    def ws_connect(self, analysis, compression_options=None):
        """Open a WebSocket connection to an analysis.

        Runs the handshake and sets ``connection.analysis_id``.

        :param analysis: name of an analysis
        """

        url = 'wss://127.0.0.1:{}/{}/ws'.format(self.get_http_port(), analysis)
        connection = yield TestConnection().connect(url, compression_options)

        self.assertEqual(len(connection.analysis_id), 8)
        raise tornado.gen.Return(connection)
