"""Simple test."""

from __future__ import absolute_import

import json
import tornado.testing

from .test_websocket import WebSocketBaseTestCase


class MultipleConnections(object):
    ANALYSIS = None

    @tornado.testing.gen_test
    def test_run(self):
        wss = []
        for _ in range(4):
            ws = yield self.ws_connect('/{}/ws'.format(self.ANALYSIS))
            wss.append(ws)
        for ws in wss:
            yield ws.write_message('{"__connect": null}')
            response = yield ws.read_message()
            r = json.loads(response)
            self.assertEqual(r['signal'], '__connect')
            self.assertIn('analysis_id', r['load'])
        for ws in wss:
            yield self.close(ws)


class MultipleConnectionsDummypi(MultipleConnections, WebSocketBaseTestCase):
    ANALYSIS = 'dummypi'


class MultipleConnectionsDummypiPy(MultipleConnections, WebSocketBaseTestCase):
    ANALYSIS = 'dummypi_py'
