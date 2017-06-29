import databench
import unittest


class TestReadme(unittest.TestCase):
    def test_md(self):
        # contains README.md
        data = databench.Readme('databench/tests/analyses/simple1')
        self.assertIn('This is the text in the `README.md` file.', data.text)
        self.assertIn('<p>This is the text in the <code>README.md</code> '
                      'file.</p>', data.html)

    def test_rst(self):
        # contains README.rst
        data = databench.Readme('databench/tests/analyses/simple2')
        self.assertEqual('Rest of readme.\n', data.text)
        self.assertIn('<p>Rest of readme.</p>', data.html)

    def test_no_readme(self):
        # contains no README
        data = databench.Readme('databench/tests/analyses/simple3')
        self.assertEqual('', data.text)
        self.assertEqual('', data.html)

    def test_unknown_dir(self):
        # directory does not exist
        data = databench.Readme('databench/tests/does_not_exist')
        self.assertEqual('', data.text)
        self.assertEqual('', data.html)
