from databench.testing import AnalysisTest
from databench.tests.analyses.parameters.analysis import Parameters
import tornado.testing


class Example(tornado.testing.AsyncTestCase):
    @tornado.testing.gen_test
    def test_gentest(self):
        test = AnalysisTest(Parameters())
        yield test.trigger('test_data', ['light', 'red'])
        self.assertIn(('data', {'light': 'red'}), test.emitted_messages)

    def test_stopwait(self):
        test = AnalysisTest(Parameters())
        test.trigger('test_data', ['light', 'red'], callback=self.stop)
        self.wait()
        self.assertIn(('data', {'light': 'red'}), test.emitted_messages)
