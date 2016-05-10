"""Websocket test."""

import databench
import json
import tornado.testing
import unittest
from zmq.eventloop.ioloop import ZMQIOLoop

from zmq.eventloop import ioloop
ioloop.install()


class WebSocketBaseTestCase(tornado.testing.AsyncHTTPTestCase):
    """similar to tornado websocket unit tests

    see https://github.com/tornadoweb/tornado/blob/master/
        tornado/test/websocket_test.py
    """
    def get_app(self):
        return databench.App().tornado_app()

    def get_new_ioloop(self):
        return ZMQIOLoop()

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


class WebSocketDatabenchTest(WebSocketBaseTestCase):
    def test_index(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertIn(b'Dummy', response.body)

    @tornado.testing.gen_test
    def test_connect(self):
        ws = yield self.ws_connect('/dummypi/ws')
        yield ws.write_message('{"__connect": null}')
        response = yield ws.read_message()
        r = json.loads(response)
        self.assertEqual(r['signal'], '__connect')
        yield self.close(ws)

    @tornado.gen.coroutine
    def _process(self, analysis='dummypi'):
        ws = yield self.ws_connect('/{}/ws'.format(analysis))

        yield ws.write_message('{"__connect": null}')
        response = yield ws.read_message()
        r = json.loads(response)
        self.assertEqual(r['signal'], '__connect')
        self.assertIn('analysis_id', r['load'])
        response = yield ws.read_message()
        r = json.loads(response)
        self.assertEqual(r['signal'], 'data')

        yield ws.write_message(
            '{"signal":"test_fn", '
            '"load":{"__process_id":123, "first_param":1}}'
        )
        response = yield ws.read_message()
        r = json.loads(response)
        self.assertEqual(r['signal'], '__process')
        self.assertEqual(r['load']['id'], 123)
        self.assertEqual(r['load']['status'], 'start')

        response = yield ws.read_message()
        r = json.loads(response)
        self.assertEqual(r['signal'], 'test_fn')
        self.assertEqual(r['load']['first_param'], 1)

        response = yield ws.read_message()
        r = json.loads(response)
        self.assertEqual(r['signal'], '__process')
        self.assertEqual(r['load']['id'], 123)
        self.assertEqual(r['load']['status'], 'end')

        yield self.close(ws)

    @tornado.testing.gen_test
    def test_process(self):
        self._process('dummypi')

    @tornado.testing.gen_test
    def test_process_py(self):
        self._process('dummypi_py')


if __name__ == '__main__':
    unittest.main()
