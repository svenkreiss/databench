"""Simple test."""

import os
import time
import signal
import requests
import websocket
import subprocess


DAEMON = None


def setup_module():
    global DAEMON

    # call os.setsid so that all subprocesses terminate when the
    # main process receives SIGTERM
    DAEMON = subprocess.Popen(['databench'],
                              close_fds=True,
                              preexec_fn=os.setsid)
    time.sleep(1)


def teardown_module():
    global DAEMON

    # simply DAEMON.terminate() would only terminate the main process,
    # but the nested processes also need to be terminated
    os.killpg(DAEMON.pid, signal.SIGTERM)


def test_get_dummypi():
    r = requests.get('http://127.0.0.1:5000/dummypi/')
    assert r.status_code == 200


def test_ws_dummypi():
    websocket.enableTrace(True)
    ws = websocket.create_connection('ws://127.0.0.1:5000/dummypi/ws')
    ws.send('{"signal":"run", "message":{"__action_id":123}}')
    r = ws.recv()
    print(r)
    assert '{"signal": "__action", ' + \
           '"message": {"status": "start", "id": 123}}' == r
    r = ws.recv()
    print(r)
    assert '{"signal": "log", "message": {"inside":' in r
    r = ws.recv()
    print(r)
    assert '{"signal": "status", "message": {"pi-uncertainty":' in r
    ws.close()


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
    ws.send('{"signal":"run", "message":{"__action_id":123}}')
    r = ws.recv()
    print(r)
    assert '{"signal": "__action", ' + \
           '"message": {"status": "start", "id": 123}}' == r
    r = ws.recv()
    print(r)
    assert '{"signal": "log", "message": {"inside":' in r
    r = ws.recv()
    print(r)
    assert '{"signal": "status", "message": {"pi-uncertainty":' in r
    ws.close()
