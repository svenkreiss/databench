"""Simple test."""

import os
import nose
import time
import signal
import requests
import subprocess

DAEMON = None
DAEMON_CNT = 0


def setup_func():
    global DAEMON, DAEMON_CNT
    if not DAEMON:
        # call os.setsid so that all subprocesses terminate when the
        # main process receives SIGTERM
        DAEMON = subprocess.Popen(['databench'], preexec_fn=os.setsid)
    time.sleep(1)
    DAEMON_CNT += 1


def teardown_func():
    global DAEMON, DAEMON_CNT
    DAEMON_CNT -= 1
    if DAEMON_CNT <= 0 and DAEMON:
        # simply DAEMON.terminate() would only terminate the main process,
        # but the nested processes also need to be terminated
        os.killpg(DAEMON.pid, signal.SIGTERM)
        DAEMON_CNT = 0


@nose.with_setup(setup_func, teardown_func)
def test_get_dummypi():
    r = requests.get('http://127.0.0.1:5000/dummypi/')
    assert r.status_code == 200
