from databench.testing import AnalysisTestCase
import tornado.testing


class Parameters(object):
    analysis = None

    @tornado.testing.gen_test
    def test_no_parameter(self):
        c = self.connection(self.analysis)
        yield c.connect()
        yield c.emit('test_action')
        r = yield c.read()
        yield c.close()

        self.assertEqual(r, {'signal': 'test_action_ack'})

    @tornado.testing.gen_test
    def test_empty_parameter(self):
        c = self.connection(self.analysis)
        yield c.connect()
        yield c.emit('test_fn', '')
        r = yield c.read()
        yield c.close()

        self.assertEqual(r, {'signal': 'test_fn', 'load': ['', 100]})

    @tornado.testing.gen_test
    def test_parameter(self):
        c = self.connection(self.analysis)
        yield c.connect()
        yield c.emit('test_fn', 1)
        r = yield c.read()
        yield c.close()

        self.assertEqual(r, {'signal': 'test_fn', 'load': [1, 100]})

    @tornado.testing.gen_test
    def test_list(self):
        c = self.connection(self.analysis)
        yield c.connect()
        yield c.emit('test_fn', [1, 2])
        r = yield c.read()
        yield c.close()

        self.assertEqual(r, {'signal': 'test_fn', 'load': [1, 2]})

    @tornado.testing.gen_test
    def test_dict(self):
        c = self.connection(self.analysis)
        yield c.connect()
        yield c.emit('test_fn', {'first_param': 1, 'second_param': 2})
        r = yield c.read()
        yield c.close()

        self.assertEqual(r, {'signal': 'test_fn', 'load': [1, 2]})

    @tornado.testing.gen_test
    def test_process(self):
        c = self.connection(self.analysis)
        yield c.connect()
        yield c.emit('test_fn', {'first_param': 1, '__process_id': 123})
        r_start = yield c.read()
        r = yield c.read()
        r_end = yield c.read()
        yield c.close()

        self.assertEqual(r_start,
                         {'signal': '__process',
                          'load': {'id': 123, 'status': 'start'}})
        self.assertEqual(r,
                         {'signal': 'test_fn',
                          'load': [1, 100]})
        self.assertEqual(r_end,
                         {'signal': '__process',
                          'load': {'id': 123, 'status': 'end'}})

    @tornado.testing.gen_test
    def test_data(self):
        data = {}
        c = self.connection(self.analysis)
        c.on('data', lambda d: data.update(d))
        yield c.connect()
        yield c.emit('test_data', ['light', 'red'])
        yield c.read()
        self.assertEqual({'light': 'red'}, data)

    @tornado.testing.gen_test
    def test_data_with_data_cb(self):
        data = {}
        c = self.connection(self.analysis)
        c.on('data', lambda d: data.update(d))
        yield c.connect()
        yield c.emit('test_data', ['light2', 'red'])
        yield c.read()
        self.assertEqual({'light2': 'red-modified'}, data)

    @tornado.testing.gen_test
    def test_class_data(self):
        data = {}
        c = self.connection(self.analysis)
        c.on('class_data', lambda d: data.update(d))
        yield c.connect()
        yield c.emit('test_class_data', ['light', 'red'])
        yield c.read()
        self.assertEqual({'light': 'red'}, data)

    @tornado.testing.gen_test
    def test_class_data_with_data_cb(self):
        data = {}
        c = self.connection(self.analysis)
        c.on('class_data', lambda d: data.update(d))
        yield c.connect()
        yield c.emit('test_class_data', ['light2', 'red'])
        yield c.read()
        self.assertEqual({'light2': 'red-modified'}, data)


class ParametersTest(Parameters, AnalysisTestCase):
    analyses_path = 'tests.analyses'
    analysis = 'parameters'


class ParametersPyTest(Parameters, AnalysisTestCase):
    analyses_path = 'tests.analyses'
    analysis = 'parameters_py'
