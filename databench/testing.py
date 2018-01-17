from .app import App
from .meta import Meta
from collections import defaultdict
import json
import tornado
from tornado.testing import AsyncHTTPTestCase, AsyncHTTPSTestCase


class AnalysisTest(object):
    """Unit test wrapper for an analysis.

    :param databench.Analysis analysis: The analysis to test.
    :param str cli_args: Command line interface arguments.
    :param str request_args: Request arguments.
    :param meta: An object with a `run_process` attribute.

    Trigger actions using the `~.trigger` method.
    All outgoing messages to the frontend are captured in `emitted_messages`.

    There are two main options for constructing tests: decorating with
    `~tornado.testing.gen_test` and ``yield`` ing futures (block until
    future is done) or to use `~tornado.testing.AsyncTestCase.wait` and
    `~tornado.testing.AsyncTestCase.stop` in callbacks.
    For detailed information on ioloops within the Tornado testing framework,
    please consult `tornado.testing`.

    Examples:

    .. literalinclude:: ../databench/tests/test_testing.py
        :language: python
    """
    def __init__(self, analysis, cli_args=None, request_args=None, meta=None):
        self.analysis = analysis
        self.analysis_instance = analysis()
        self.cli_args = cli_args
        self.request_args = request_args
        self.meta = meta or Meta
        self.emitted_messages = []

        Meta.fill_action_handlers(analysis)

        # initialize
        self.analysis_instance.init_databench()
        self.analysis_instance.set_emit_fn(self.emulate_emit_to_frontend)
        self.trigger('connect')
        self.trigger('args', [cli_args, request_args])
        self.trigger('connected')

    def emulate_emit_to_frontend(self, signal, message):
        self.emitted_messages.append((signal, message))

    def trigger(self, action_name, message='__nomessagetoken__', **kwargs):
        """Trigger an `on` callback.

        :param str action_name: Name of the action to trigger.
        :param message: Message.
        :param callback:
            A callback function when done (e.g.
            `~tornado.testing.AsyncTestCase.stop` in tests).
        :rtype: tornado.concurrent.Future
        """
        return self.meta.run_process(
            self.analysis_instance, action_name, message, **kwargs)


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
        self.messages = defaultdict(list)

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
        self.messages[message.get('signal', '__no_signal__')].append(
            message.get('load', '__no_load__'))

        raise tornado.gen.Return(message)


class ConnectionTestCase(AsyncHTTPTestCase):
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

    def connection(self, analysis_name=None, analysis_id=None,
                   request_args=None):
        """Create a WebSocket connection to the backend.

        :rtype: Connection
        """
        path = '{}/'.format(analysis_name) if analysis_name else ''
        url = 'ws://127.0.0.1:{}/{}ws'.format(self.get_http_port(), path)
        return Connection(url, analysis_id, request_args)

    def connect(self, analysis_name=None, analysis_id=None, request_args=None):
        """Create a WebSocket connection to the backend and connect to it.

        :rtype: tornado.concurrent.Future
        """
        return self.connection(analysis_name, analysis_id,
                               request_args).connect()


class ConnectionTestCaseSSL(AsyncHTTPSTestCase):
    """Same as :class:`ConnectionTestCase` but with SSL."""

    analyses_path = None

    def get_app(self):
        return App(self.analyses_path).tornado_app()

    def connection(self, analysis_name=None, analysis_id=None,
                   request_args=None):
        path = '{}/'.format(analysis_name) if analysis_name else ''
        url = 'wss://127.0.0.1:{}/{}ws'.format(self.get_http_port(), path)
        return Connection(url, analysis_id, request_args)

    def connect(self, analysis_name=None, analysis_id=None, request_args=None):
        return self.connection(analysis_name, analysis_id,
                               request_args).connect()
