"""Simple test."""

import os
import requests
import signal
import subprocess
import time
import unittest


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

    def test_main(self):
        r = requests.get('http://127.0.0.1:5000/')
        assert r.status_code == 200


if __name__ == '__main__':
    unittest.main()
