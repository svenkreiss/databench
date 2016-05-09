"""Simple test."""

import databench
import json
import os
import requests
import signal
import subprocess
import time
import tornado.testing
import unittest
import websocket


LOGLEVEL = 'DEBUG'


class Dummypi(unittest.TestCase):
    def setUp(self):
        # call os.setsid so that all subprocesses terminate when the
        # main process receives SIGTERM
        self.daemon = subprocess.Popen(['databench', '--with-coverage',
                                        '--log={}'.format(LOGLEVEL)],
                                       close_fds=True,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       preexec_fn=os.setsid)
        time.sleep(5)

    def tearDown(self):
        # simply DAEMON.terminate() would only terminate the main process,
        # but the nested processes also need to be terminated
        if hasattr(signal, 'SIGINT'):
            os.killpg(self.daemon.pid, signal.SIGINT)
        else:
            os.killpg(self.daemon.pid, signal.SIGTERM)
        time.sleep(5)
        self.daemon.wait()

    """

    Testing a default Python analysis
    ---------------------------------
    """

    def test_get_dummypi(self):
        r = requests.get('http://127.0.0.1:5000/dummypi/')
        assert r.status_code == 200

    def test_ws_dummypi(self):
        # websocket.enableTrace(True)
        ws = websocket.create_connection('ws://127.0.0.1:5000/dummypi/ws')
        ws.send('{"__connect": null}')
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == '__connect'
        assert 'analysis_id' in r['load']
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == 'data'
        assert 'samples' in r['load']
        ws.send('{"signal":"run", "load":{"__process_id":123}}')
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == '__process'
        assert r['load']['id'] == 123
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == 'log'
        assert 'inside' in r['load']
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == 'data'
        assert 'pi' in r['load']
        ws.close()

    def test_multiple_ws_dummypi(self):
        # websocket.enableTrace(True)
        wss = [websocket.create_connection('ws://127.0.0.1:5000/dummypi/ws')
               for _ in range(4)]
        for ws in wss:
            ws.send('{"__connect": null}')
            r = json.loads(ws.recv())
            print(r)
            assert r['signal'] == '__connect'
            assert 'analysis_id' in r['load']
        for ws in wss:
            ws.close()

    """

    Python Language Kernel tests
    ----------------------------
    """

    def test_get_dummypi_py(self):
        r = requests.get('http://127.0.0.1:5000/dummypi_py/')
        assert r.status_code == 200
        # in tests that dont engage the langauge kernel, wait for the kernel
        # to initialize before closing it again
        time.sleep(1)

    def test_multiple_ws_dummypi_py(self):
        # websocket.enableTrace(True)
        wss = [websocket.create_connection('ws://127.0.0.1:5000/dummypi_py/ws')
               for _ in range(4)]
        for ws in wss:
            ws.send('{"__connect": null}')
            r = json.loads(ws.recv())
            print(r)
            assert r['signal'] == '__connect'
            assert 'analysis_id' in r['load']
        # in tests that dont engage the langauge kernel, wait for the kernel
        # to initialize before closing it again
        time.sleep(1)
        for ws in wss:
            ws.close()

    def test_ws_dummypi_py(self):
        # websocket.enableTrace(True)
        ws = websocket.create_connection('ws://127.0.0.1:5000/dummypi_py/ws')
        ws.send('{"__connect": null}')
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == '__connect'
        assert 'analysis_id' in r['load']
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == 'data'
        assert 'samples' in r['load']
        ws.send('{"signal":"run", "load":{"__process_id":123}}')
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == '__process'
        assert r['load']['id'] == 123
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == 'log'
        assert 'inside' in r['load']
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == 'data'
        assert 'pi' in r['load']
        ws.close()

    """

    Function Argument Tests
    -----------------------
    """

    def _fn_call(self, name='dummypi'):
        # websocket.enableTrace(True)
        ws = websocket.create_connection('ws://127.0.0.1:5000/{}/ws'
                                         ''.format(name))
        ws.send('{"__connect": null}')
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == '__connect'
        assert 'analysis_id' in r['load']
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == 'data'
        assert 'samples' in r['load']
        ws.send('{"signal":"test_fn", "load": 1}')
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == 'test_fn'
        assert r['load']['first_param'] == 1
        assert r['load']['second_param'] == 100
        ws.close()

    def _fn_call_array(self, name='dummypi'):
        # websocket.enableTrace(True)
        ws = websocket.create_connection('ws://127.0.0.1:5000/{}/ws'
                                         ''.format(name))
        ws.send('{"__connect": null}')
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == '__connect'
        assert 'analysis_id' in r['load']
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == 'data'
        assert 'samples' in r['load']
        ws.send('{"signal":"test_fn", "load": [1, 2]}')
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == 'test_fn'
        assert r['load']['first_param'] == 1
        assert r['load']['second_param'] == 2
        ws.close()

    def _fn_call_dict(self, name='dummypi'):
        # websocket.enableTrace(True)
        ws = websocket.create_connection('ws://127.0.0.1:5000/{}/ws'
                                         ''.format(name))
        ws.send('{"__connect": null}')
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == '__connect'
        assert 'analysis_id' in r['load']
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == 'data'
        assert 'samples' in r['load']
        ws.send('{"signal":"test_fn", "load": '
                '{"first_param": 1, "second_param": 2}}')
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == 'test_fn'
        assert r['load']['first_param'] == 1
        assert r['load']['second_param'] == 2
        ws.close()

    def test_fn_call_dummypi(self):
        self._fn_call()

    def test_fn_call_dummypi_array(self):
        self._fn_call_array()

    def test_fn_call_dummypi_dict(self):
        self._fn_call_dict()

    def test_fn_call_dummypi_py(self):
        self._fn_call(name='dummypi_py')

    def test_fn_call_dummypi_py_array(self):
        self._fn_call_array(name='dummypi_py')

    def test_fn_call_dummypi_py_dict(self):
        self._fn_call_dict(name='dummypi_py')


class WebSocketBaseTestCase(tornado.testing.AsyncHTTPTestCase):
    """similar to tornado websocket unit tests

    see https://github.com/tornadoweb/tornado/blob/master/
        tornado/test/websocket_test.py
    """
    @tornado.gen.coroutine
    def ws_connect(self, path, compression_options=None):
        ws = yield tornado.websocket.websocket_connect(
            'ws://127.0.0.1:%d%s' % (self.get_http_port(), path),
            compression_options=compression_options)
        raise tornado.gen.Return(ws)

    @tornado.gen.coroutine
    def close(self, ws):
        """Close a websocket connection and wait for the server side.

        If we don't wait here, there are sometimes leak warnings in the
        tests.
        """
        ws.close()
        # yield self.close_future


class WebSocketDatabenchTest(WebSocketBaseTestCase):
    def get_app(self):
        # self.close_future = tornado.concurrent.Future()
        app = databench.App().tornado_app()
        return app

    def test_index(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertIn(b'Simple1', response.body)

    @tornado.testing.gen_test
    def test_websocket_gen(self):
        ws = yield self.ws_connect('/simple1/ws')
        yield ws.write_message('{"__connect": null}')
        response = yield ws.read_message()
        r = json.loads(response)
        self.assertEqual(r['signal'], '__connect')
        yield self.close(ws)


if __name__ == '__main__':
    unittest.main()
