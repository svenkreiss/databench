import os
import signal
import subprocess
import time
import unittest


LOGLEVEL = 'WARNING'


class NodeClient(unittest.TestCase):
    def setUp(self):
        # transpile js code for node
        subprocess.call(['gulp', 'node_client'])

        # call os.setsid so that all subprocesses terminate when the
        # main process receives SIGTERM
        self.daemon = subprocess.Popen(['databench',
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

    def test_node_client(self):
        subprocess.check_call(['npm', 'test'])


if __name__ == '__main__':
    unittest.main()
