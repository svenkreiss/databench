from databench.testing import AnalysisTest
from databench.tests.analyses.parameters.analysis import Parameters
import unittest


class Example(unittest.TestCase):
    def test_data(self):
        test = AnalysisTest(Parameters())
        test.trigger('test_data', ['light', 'red'])
        self.assertIn(('data', {'light': 'red'}), test.emitted_messages)

    def test_process(self):
        test = AnalysisTest(Parameters())
        test.trigger('test_data', {'key': 'light',
                                   'value': 'red',
                                   '__process_id': 3})
        self.assertEqual([
            ('__process', {'id': 3, 'status': 'start'}),
            ('data', {'light': 'red'}),
            ('__process', {'id': 3, 'status': 'end'}),
        ], test.emitted_messages)
