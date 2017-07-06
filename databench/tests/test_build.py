import databench
import os
import subprocess
import time
import unittest


_, ANALYSES_PATH = databench.App.get_analyses('databench.tests.analyses')
_, ANALYSES_BROKEN_PATH = databench.App.get_analyses(
    'databench.tests.analyses_broken')


class Build(unittest.TestCase):
    def file_id(self, filename=None):
        if filename is None:
            filename = os.path.join(ANALYSES_PATH, 'build_test.txt')
        if os.path.exists(filename):
            return '{}'.format(os.path.getmtime(filename))
        return 'file_not_found'

    def setUp(self):
        self.original_working_dir = os.getcwd()  # original working directory
        self.coverage_file = os.path.join(os.getcwd(), '.coverage')

    def tearDown(self):
        os.chdir(self.original_working_dir)

    def test_build(self):
        before = self.file_id()

        os.chdir(os.path.join(ANALYSES_PATH, '..', '..'))
        subprocess.check_call(['databench', '--build',
                               '--analyses', 'tests.analyses',
                               '--coverage', self.coverage_file])
        os.chdir(self.original_working_dir)

        time.sleep(1)
        after = self.file_id()
        self.assertNotEqual(before, after)

    def test_cwd_outside_analyses(self):
        before = self.file_id()

        os.chdir(os.path.join(ANALYSES_PATH, '..'))
        subprocess.check_call(['databench', '--build',
                               '--coverage', self.coverage_file])
        os.chdir(self.original_working_dir)

        time.sleep(1)
        after = self.file_id()
        self.assertNotEqual(before, after)

    def test_cwd_inside_analyses(self):
        before = self.file_id()

        os.chdir(ANALYSES_PATH)
        subprocess.check_call(['databench', '--build',
                               '--coverage', self.coverage_file])
        os.chdir(self.original_working_dir)

        time.sleep(1)
        after = self.file_id()
        self.assertNotEqual(before, after)

    def test_broken_analyses(self):
        build_file = os.path.join(ANALYSES_BROKEN_PATH, 'build_test.txt')
        before = self.file_id(build_file)

        os.chdir(os.path.join(ANALYSES_BROKEN_PATH, '..', '..'))
        subprocess.check_call(['databench', '--build',
                               '--analyses', 'tests.analyses_broken',
                               '--coverage', self.coverage_file])
        os.chdir(self.original_working_dir)

        time.sleep(1)
        after = self.file_id(build_file)
        self.assertNotEqual(before, after)
