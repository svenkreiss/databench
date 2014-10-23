"""Simple test."""

import os
import time
import signal
import requests
import websocket
import subprocess


"""

Starting and stopping 'databench'
---------------------------------
"""


DAEMON = None


def setup_module():
    global DAEMON

    # call os.setsid so that all subprocesses terminate when the
    # main process receives SIGTERM
    DAEMON = subprocess.Popen(['databench', '--with-coverage'],
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
    websocket.enableTrace(True)
    ws = websocket.create_connection('ws://127.0.0.1:5000/dummypi/ws')
    ws.send('{"signal":"run", "load":{"__action_id":123}}')
    r = ws.recv()
    print(r)
    assert '"load": {"status": "start", "id": 123}' in r
    assert '"signal": "__action"' in r
    r = ws.recv()
    print(r)
    assert '"signal": "log"' in r
    assert '"load": {"inside":' in r
    r = ws.recv()
    print(r)
    assert '"signal": "status"' in r
    assert '"load": {"pi-uncertainty":' in r
    ws.close()


def test_zip_dummypi():
    r = requests.get('http://127.0.0.1:5000/dummypi/dummypi.zip')
    assert r.status_code == 200


"""

Python Language Kernel tests
----------------------------
"""


def test_get_dummypi_py():
    r = requests.get('http://127.0.0.1:5000/dummypi_py/')
    assert r.status_code == 200


def test_ws_dummypi_py():
    websocket.enableTrace(True)
    ws = websocket.create_connection('ws://127.0.0.1:5000/dummypi_py/ws')
    ws.send('{"signal":"run", "load":{"__action_id":123}}')
    r = ws.recv()
    print(r)
    assert '"load": {"status": "start", "id": 123}' in r
    assert '"signal": "__action"' in r
    r = ws.recv()
    print(r)
    assert '"signal": "log"' in r
    assert '"load": {"inside":' in r
    r = ws.recv()
    print(r)
    assert '"signal": "status"' in r
    assert '"load": {"pi-uncertainty":' in r
    ws.close()


"""

Function Argument Tests
-----------------------
"""


def _fn_call(name='dummypi'):
    websocket.enableTrace(True)
    ws = websocket.create_connection('ws://127.0.0.1:5000/'+name+'/ws')
    ws.send('{"signal":"test_fn", "load": 1}')
    r = ws.recv()
    print(r)
    assert '"signal": "test_fn"' in r
    assert '"load": {"first_param": 1, "second_param": 100}' in r
    ws.close()


def _fn_call_array(name='dummypi'):
    websocket.enableTrace(True)
    ws = websocket.create_connection('ws://127.0.0.1:5000/'+name+'/ws')
    ws.send('{"signal":"test_fn", "load": [1, 2]}')
    r = ws.recv()
    print(r)
    assert '"signal": "test_fn"' in r
    assert '"load": {"first_param": 1, "second_param": 2}' in r
    ws.close()


def _fn_call_dict(name='dummypi'):
    websocket.enableTrace(True)
    ws = websocket.create_connection('ws://127.0.0.1:5000/'+name+'/ws')
    ws.send('{"signal":"test_fn", "load": '
            '{"first_param": 1, "second_param": 2}}')
    r = ws.recv()
    print(r)
    assert '"signal": "test_fn"' in r
    assert '"load": {"first_param": 1, "second_param": 2}' in r
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
