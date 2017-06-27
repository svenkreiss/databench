"""Websocket test."""

from databench.testing import AnalysisTestCase, AnalysisTestCaseSSL, gen_test


class Basics(object):
    def test_index(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertIn(b'Dummy', response.body)

    @gen_test
    def test_connect(self):
        c = yield self.connection(self.analysis).connect()
        yield c.close()
        self.assertEqual(len(c.analysis_id), 8)


class BasicsDummypi(Basics, AnalysisTestCase):
    analysis = 'dummypi'


class BasicsDummypiPy(Basics, AnalysisTestCase):
    analysis = 'dummypi_py'


class BasicsDummypiSSL(Basics, AnalysisTestCaseSSL):
    analysis = 'dummypi'


class BasicsDummypiPySSL(Basics, AnalysisTestCaseSSL):
    analysis = 'dummypi_py'


class BasicsTestAnalyses(AnalysisTestCase):
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

    @gen_test
    def test_connection_interruption(self):
        conn1 = yield self.connection('connection_interruption').connect()
        yield conn1.close()
        analysis_id1 = conn1.analysis_id
        self.assertEqual(len(analysis_id1), 8)

        conn2 = yield self.connection('connection_interruption',
                                      analysis_id1).connect()
        yield conn2.close()
        analysis_id2 = conn2.analysis_id
        self.assertEqual(analysis_id1, analysis_id2)
