import os
import signal
import subprocess
import time


DAEMON = None
LOGLEVEL = 'WARNING'


def setup_module():
    global DAEMON

    # transpile js code for node
    subprocess.call(['gulp', 'node_client'])

    # call os.setsid so that all subprocesses terminate when the
    # main process receives SIGTERM
    DAEMON = subprocess.Popen(['databench',
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


def test_node_client():
    subprocess.check_call(['npm', 'test'])


if __name__ == '__main__':
    setup_module()
    test_node_client()
    teardown_module()
