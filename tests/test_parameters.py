import databench
import tornado.testing


class Parameters(object):
    analysis = None

    @tornado.testing.gen_test
    def test_parameter(self):
        yield self.ws_connect(self.analysis)

        self.emit('test_fn', 1)

        r = yield self.read()
        self.assertEqual(r, {'signal': 'test_fn', 'load': [1, 100]})

        yield self.close()

    @tornado.testing.gen_test
    def test_list(self):
        yield self.ws_connect(self.analysis)

        self.emit('test_fn', [1, 2])

        r = yield self.read()
        self.assertEqual(r, {'signal': 'test_fn', 'load': [1, 2]})

        yield self.close()

    @tornado.testing.gen_test
    def test_dict(self):
        yield self.ws_connect(self.analysis)

        self.emit('test_fn', {'first_param': 1, 'second_param': 2})

        r = yield self.read()
        self.assertEqual(r, {'signal': 'test_fn', 'load': [1, 2]})

        yield self.close()

    @tornado.testing.gen_test
    def test_process(self):
        yield self.ws_connect(self.analysis)

        self.emit('test_fn', {'first_param': 1, '__process_id': 123})
        r = yield self.read()
        self.assertEqual(r, {'signal': '__process',
                             'load': {'id': 123, 'status': 'start'}})

        r = yield self.read()
        self.assertEqual(r, {'signal': 'test_fn', 'load': [1, 100]})

        r = yield self.read()
        self.assertEqual(r, {'signal': '__process',
                             'load': {'id': 123, 'status': 'end'}})

        yield self.close()


class ParametersTest(Parameters, databench.AnalysisTestCase):
    analyses_path = 'tests.analyses'
    analysis = 'parameters'


class ParametersPyTest(Parameters, databench.AnalysisTestCase):
    analyses_path = 'tests.analyses'
    analysis = 'parameters_py'
