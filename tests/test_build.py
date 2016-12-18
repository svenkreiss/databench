import os
import subprocess
import time
import unittest


class Build(unittest.TestCase):
    def file_id(self, filename='tests/analyses/build_test.txt'):
        if os.path.exists(filename):
            return '{}'.format(os.path.getmtime(filename))
        return 'file_not_found'

    def setUp(self):
        self.owd = os.getcwd()  # original working directory

    def tearDown(self):
        os.chdir(self.owd)

    def test_build(self):
        before = self.file_id()
        subprocess.check_call(['databench', '--build',
                               '--analyses', 'tests.analyses',
                               '--coverage', '.coverage'])
        time.sleep(1)
        after = self.file_id()
        self.assertNotEqual(before, after)

    def test_cwd_outside_analyses(self):
        before = self.file_id()

        os.chdir('tests')
        subprocess.check_call(['databench', '--build',
                               '--coverage', '../.coverage'])
        os.chdir(self.owd)

        time.sleep(1)
        after = self.file_id()
        self.assertNotEqual(before, after)

    def test_cwd_inside_analyses(self):
        before = self.file_id()

        os.chdir(os.path.join('tests', 'analyses'))
        subprocess.check_call(['databench', '--build',
                               '--coverage', '../../.coverage'])
        os.chdir(self.owd)

        time.sleep(1)
        after = self.file_id()
        self.assertNotEqual(before, after)

    def test_broken_analyses(self):
        before = self.file_id(filename='tests/analyses_broken/build_test.txt')
        subprocess.check_call(['databench', '--build',
                               '--analyses', 'tests.analyses_broken',
                               '--coverage', '.coverage'])
        time.sleep(1)
        after = self.file_id(filename='tests/analyses_broken/build_test.txt')
        self.assertNotEqual(before, after)
