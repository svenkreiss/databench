import databench
from databench.analyses_packaged.dummypi.analysis import Dummypi
from databench.testing import AnalysisTest
import tornado.testing


class Parameters(databench.Analysis):
    @databench.on
    def test_data(self, key, value):
        yield self.set_state({key: value})


class Example(tornado.testing.AsyncTestCase):
    @tornado.testing.gen_test
    def test_data(self):
        test = AnalysisTest(Parameters)
        yield test.trigger('test_data', ['light', 'red'])
        self.assertIn(('data', {'light': 'red'}), test.emitted_messages)

    @tornado.testing.gen_test
    def test_process(self):
        test = AnalysisTest(Parameters)
        yield test.trigger('test_data', {'key': 'light',
                                         'value': 'red',
                                         '__process_id': 3})
        self.assertEqual([
            ('__process', {'id': 3, 'status': 'start'}),
            ('data', {'light': 'red'}),
            ('__process', {'id': 3, 'status': 'end'}),
        ], test.emitted_messages)

    @tornado.testing.gen_test
    def test_multiple_emits(self):
        test = AnalysisTest(Dummypi)
        yield test.trigger('run')
        self.assertIn(('log', {'action': 'done'}), test.emitted_messages)
