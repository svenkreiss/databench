import databench.tests.analyses
import databench.tests.analyses_broken
import os
import subprocess
import time
import unittest


ANALYSES_PATH = os.path.abspath(
    os.path.dirname(databench.tests.analyses.__file__))
ANALYSES_BROKEN_PATH = os.path.abspath(
    os.path.dirname(databench.tests.analyses_broken.__file__))


class Build(unittest.TestCase):
    def file_id(self, filename=None):
        if filename is None:
            filename = os.path.join(ANALYSES_PATH, 'build_test.txt')
        if os.path.exists(filename):
            return '{}'.format(os.path.getmtime(filename))
        return 'file_not_found'

    def setUp(self):
        self.original_working_dir = os.getcwd()  # original working directory

    def tearDown(self):
        os.chdir(self.original_working_dir)

    def test_build(self):
        before = self.file_id()

        subprocess.check_call(['databench', '--build',
                               '--analyses', 'databench.tests.analyses',
                               '--coverage', '.coverage'])

        time.sleep(1)
        after = self.file_id()
        self.assertNotEqual(before, after)

    def test_cwd_outside_analyses(self):
        before = self.file_id()

        os.chdir(os.path.join(ANALYSES_PATH, '..'))
        subprocess.check_call(['databench', '--build',
                               '--coverage', '../../.coverage'])
        os.chdir(self.original_working_dir)

        time.sleep(1)
        after = self.file_id()
        self.assertNotEqual(before, after)

    def test_cwd_inside_analyses(self):
        before = self.file_id()

        os.chdir(ANALYSES_PATH)
        subprocess.check_call(['databench', '--build',
                               '--coverage', '../../../.coverage'])
        os.chdir(self.original_working_dir)

        time.sleep(1)
        after = self.file_id()
        self.assertNotEqual(before, after)

    def test_broken_analyses(self):
        build_file = os.path.join(ANALYSES_BROKEN_PATH, 'build_test.txt')
        before = self.file_id(build_file)

        subprocess.check_call(['databench', '--build',
                               '--analyses', 'databench.tests.analyses_broken',
                               '--coverage', '.coverage'])

        time.sleep(1)
        after = self.file_id(build_file)
        self.assertNotEqual(before, after)
