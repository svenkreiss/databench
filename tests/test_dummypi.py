"""Simple test."""

import json
import test_websocket
import tornado.testing
import unittest


class MultipleConnections(test_websocket.WebSocketBaseTestCase):

    @tornado.gen.coroutine
    def _run(self, analysis='dummypi'):
        wss = []
        for _ in range(4):
            ws = yield self.ws_connect('/{}/ws'.format(analysis))
            wss.append(ws)
        for ws in wss:
            yield ws.write_message('{"__connect": null}')
            response = yield ws.read_message()
            r = json.loads(response)
            self.assertEqual(r['signal'], '__connect')
            self.assertIn('analysis_id', r['load'])
        for ws in wss:
            yield self.close(ws)

    @tornado.testing.gen_test
    def test_(self):
        self._run('dummypi')

    @tornado.testing.gen_test
    def test_py(self):
        self._run('dummypi_py')


class ParameterTest(test_websocket.WebSocketBaseTestCase):

    @tornado.gen.coroutine
    def _parameter(self, analysis='dummypi'):
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
            '{"signal":"test_fn", "load":1}'
        )
        response = yield ws.read_message()
        r = json.loads(response)
        self.assertEqual(r['signal'], 'test_fn')
        self.assertEqual(r['load']['first_param'], 1)

        yield self.close(ws)

    @tornado.gen.coroutine
    def _list(self, analysis='dummypi'):
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
            '{"signal":"test_fn", "load":[1, 2]}'
        )
        response = yield ws.read_message()
        r = json.loads(response)
        self.assertEqual(r['signal'], 'test_fn')
        self.assertEqual(r['load']['first_param'], 1)
        self.assertEqual(r['load']['second_param'], 2)

        yield self.close(ws)

    @tornado.gen.coroutine
    def _dict(self, analysis='dummypi'):
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
            '{"signal":"test_fn", "load":{"first_param":1, "second_param":2}}'
        )
        response = yield ws.read_message()
        r = json.loads(response)
        self.assertEqual(r['signal'], 'test_fn')
        self.assertEqual(r['load']['first_param'], 1)
        self.assertEqual(r['load']['second_param'], 2)

        yield self.close(ws)

    @tornado.testing.gen_test
    def test_parameter(self):
        self._parameter('dummypi')

    @tornado.testing.gen_test
    def test_parameter_py(self):
        self._parameter('dummypi_py')

    @tornado.testing.gen_test
    def test_list(self):
        self._list('dummypi')

    @tornado.testing.gen_test
    def test_list_py(self):
        self._list('dummypi_py')

    @tornado.testing.gen_test
    def test_dict(self):
        self._dict('dummypi')

    @tornado.testing.gen_test
    def test_dict_py(self):
        self._dict('dummypi_py')


if __name__ == '__main__':
    unittest.main()
