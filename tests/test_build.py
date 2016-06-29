import os
import subprocess
import unittest


class Build(unittest.TestCase):
    def file_id(self, filename='build_test.txt'):
        if os.path.exists(filename):
            return '{}'.format(os.path.getmtime(filename))
        return 'file_not_found'

    def test_build(self):
        before = self.file_id()
        subprocess.check_call(['databench',
                               '--build',
                               '--analyses', 'tests.analyses'])
        after = self.file_id()
        self.assertNotEqual(before, after)
