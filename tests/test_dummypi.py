"""Simple test."""

import json
import os
import requests
import signal
import subprocess
import time
import websocket


DAEMON = None
LOGLEVEL = 'DEBUG'


def setup_module():
    global DAEMON

    # call os.setsid so that all subprocesses terminate when the
    # main process receives SIGTERM
    DAEMON = subprocess.Popen(['databench', '--with-coverage',
                               '--log={}'.format(LOGLEVEL)],
                              close_fds=True,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              preexec_fn=os.setsid)
    time.sleep(1)


def teardown_module():
    global DAEMON

    # simply DAEMON.terminate() would only terminate the main process,
    # but the nested processes also need to be terminated
    #
    # SIGUSR1 does not exist on Windows
    if hasattr(signal, 'SIGUSR1'):
        os.killpg(DAEMON.pid, signal.SIGUSR1)
    else:
        os.killpg(DAEMON.pid, signal.SIGTERM)
    DAEMON.wait()


"""

Testing a default Python analysis
---------------------------------
"""


def test_get_dummypi():
    r = requests.get('http://127.0.0.1:5000/dummypi/')
    assert r.status_code == 200


def test_ws_dummypi():
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
    ws.send('{"signal":"run", "load":{"__action_id":123}}')
    r = json.loads(ws.recv())
    print(r)
    assert r['signal'] == '__action'
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


def test_multiple_ws_dummypi():
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


def test_get_dummypi_py():
    r = requests.get('http://127.0.0.1:5000/dummypi_py/')
    assert r.status_code == 200


def test_multiple_ws_dummypi_py():
    # websocket.enableTrace(True)
    wss = [websocket.create_connection('ws://127.0.0.1:5000/dummypi_py/ws')
           for _ in range(4)]
    for ws in wss:
        ws.send('{"__connect": null}')
        r = json.loads(ws.recv())
        print(r)
        assert r['signal'] == '__connect'
        assert 'analysis_id' in r['load']
    for ws in wss:
        ws.close()


def test_ws_dummypi_py():
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
    ws.send('{"signal":"run", "load":{"__action_id":123}}')
    r = json.loads(ws.recv())
    print(r)
    assert r['signal'] == '__action'
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


def _fn_call(name='dummypi'):
    # websocket.enableTrace(True)
    ws = websocket.create_connection('ws://127.0.0.1:5000/{}/ws'.format(name))
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


def _fn_call_array(name='dummypi'):
    # websocket.enableTrace(True)
    ws = websocket.create_connection('ws://127.0.0.1:5000/{}/ws'.format(name))
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


def _fn_call_dict(name='dummypi'):
    # websocket.enableTrace(True)
    ws = websocket.create_connection('ws://127.0.0.1:5000/{}/ws'.format(name))
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


def test_fn_call_dummypi():
    _fn_call()


def test_fn_call_dummypi_array():
    _fn_call_array()


def test_fn_call_dummypi_dict():
    _fn_call_dict()


def test_fn_call_dummypi_py():
    _fn_call(name='dummypi_py')


def test_fn_call_dummypi_py_array():
    _fn_call_array(name='dummypi_py')


def test_fn_call_dummypi_py_dict():
    _fn_call_dict(name='dummypi_py')


if __name__ == '__main__':
    setup_module()
    test_ws_dummypi_py()
    teardown_module()
