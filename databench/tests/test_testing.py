from databench.testing import AnalysisTestCase, gen_test


class Example(AnalysisTestCase):
    analyses_path = 'databench.tests.analyses'

    @gen_test
    def test_data(self):
        c = yield self.connection(analysis_name='parameters').connect()
        yield c.emit('test_data', ['light', 'red'])
        yield c.read()
        self.assertEqual({'light': 'red'}, c.data)
        yield c.close()
