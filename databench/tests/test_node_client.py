import subprocess
import unittest


class NodeClient(unittest.TestCase):
    def setUp(self):
        # transpile js code for node
        subprocess.call(['npm', 'run', 'build'])

    def test_node_client(self):
        subprocess.check_call(['npm', 'test'])


if __name__ == '__main__':
    unittest.main()
