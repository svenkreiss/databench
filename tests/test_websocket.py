"""Websocket test."""

import databench
import json
import tornado.testing
import unittest


class WebSocketBaseTestCase(tornado.testing.AsyncHTTPTestCase):
    """similar to tornado websocket unit tests

    see https://github.com/tornadoweb/tornado/blob/master/
        tornado/test/websocket_test.py
    """
    def get_app(self):
        return databench.App().tornado_app()

    @tornado.gen.coroutine
    def ws_connect(self, path, compression_options=None):
        ws = yield tornado.websocket.websocket_connect(
            'ws://127.0.0.1:%d%s' % (self.get_http_port(), path),
            # io_loop=self.io_loop,
            compression_options=compression_options)
        raise tornado.gen.Return(ws)

    @tornado.gen.coroutine
    def close(self, ws):
        """Close a websocket connection and wait for the server side.

        If we don't wait here, there are sometimes leak warnings in the
        tests.
        """
        ws.close()
        yield tornado.gen.sleep(1.0)


class Basics(object):
    ANALYSIS = None

    def test_index(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertIn(b'Dummy', response.body)

    @tornado.testing.gen_test
    def test_connect(self):
        ws = yield self.ws_connect('/{}/ws'.format(self.ANALYSIS))
        yield ws.write_message('{"__connect": null}')
        response = yield ws.read_message()
        r = json.loads(response)
        self.assertEqual(r['signal'], '__connect')
        yield self.close(ws)


class BasicsDummypi(Basics, WebSocketBaseTestCase):
    ANALYSIS = 'dummypi'


class BasicsDummypiPy(Basics, WebSocketBaseTestCase):
    ANALYSIS = 'dummypi_py'


class BasicsTestAnalyses(WebSocketBaseTestCase):
    def get_app(self):
        return databench.App('tests.analyses').tornado_app()

    def test_index(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertIn(b'simple1', response.body)

    def test_static_file(self):
        response = self.fetch('/static/test_file.txt')
        self.assertEqual(response.code, 200)
        self.assertIn(b'placeholder', response.body)

    def test_node_modules_file(self):
        response = self.fetch('/node_modules/test_file.txt')
        self.assertEqual(response.code, 200)
        self.assertIn(b'placeholder', response.body)


if __name__ == '__main__':
    unittest.main()
