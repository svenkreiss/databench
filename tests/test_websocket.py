"""Websocket test."""

import databench
import tornado.testing


class Basics(object):
    ANALYSIS = None

    def test_index(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertIn(b'Dummy', response.body)

    @tornado.testing.gen_test
    def test_connect(self):
        c = yield self.ws_connect(self.analysis)
        yield c.close()
        self.assertEqual(len(c.analysis_id), 8)


class BasicsDummypi(Basics, databench.AnalysisTestCase):
    analysis = 'dummypi'


class BasicsDummypiPy(Basics, databench.AnalysisTestCase):
    analysis = 'dummypi_py'


class BasicsDummypiSSL(Basics, databench.AnalysisTestCaseSSL):
    analysis = 'dummypi'


class BasicsDummypiPySSL(Basics, databench.AnalysisTestCaseSSL):
    analysis = 'dummypi_py'


class BasicsTestAnalyses(databench.AnalysisTestCase):
    analyses_path = 'tests.analyses'

    def test_index(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertIn(b'simple1', response.body)

    def test_static_file(self):
        response = self.fetch('/static/test_file.txt')
        self.assertEqual(response.code, 200)
        self.assertIn(b'placeholder', response.body)

    def test_node_modules_file(self):
        response = self.fetch('/node_modules/test_file.txt')
        self.assertEqual(response.code, 200)
        self.assertIn(b'placeholder', response.body)
