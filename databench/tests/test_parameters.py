from databench.testing import ConnectionTestCase
import tornado.testing


class ParametersTestCases(object):
    analysis = None

    @tornado.testing.gen_test
    def test_no_parameter(self):
        c = yield self.connect(self.analysis)
        yield c.emit('test_action')
        r = yield c.read()
        yield c.close()

        self.assertEqual(r, {'signal': 'test_action_ack'})

    @tornado.testing.gen_test
    def test_empty_parameter(self):
        c = yield self.connect(self.analysis)
        yield c.emit('test_fn', '')
        r = yield c.read()
        yield c.close()

        self.assertEqual(r, {'signal': 'test_fn', 'load': ['', 100]})

    @tornado.testing.gen_test
    def test_parameter(self):
        c = yield self.connect(self.analysis)
        yield c.emit('test_fn', 1)
        r = yield c.read()
        yield c.close()

        self.assertEqual(r, {'signal': 'test_fn', 'load': [1, 100]})

    @tornado.testing.gen_test
    def test_list(self):
        c = yield self.connect(self.analysis)
        yield c.emit('test_fn', [1, 2])
        r = yield c.read()
        yield c.close()

        self.assertEqual(r, {'signal': 'test_fn', 'load': [1, 2]})

    @tornado.testing.gen_test
    def test_dict(self):
        c = yield self.connect(self.analysis)
        yield c.emit('test_fn', {'first_param': 1, 'second_param': 2})
        r = yield c.read()
        yield c.close()

        self.assertEqual(r, {'signal': 'test_fn', 'load': [1, 2]})

    @tornado.testing.gen_test
    def test_process(self):
        c = yield self.connect(self.analysis)
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
        c = yield self.connect(self.analysis)
        yield c.emit('test_data', ['light', 'red'])
        yield c.read()
        self.assertEqual({'light': 'red'}, c.data)
        yield c.close()

    @tornado.testing.gen_test
    def test_set_data(self):
        c = yield self.connect(self.analysis)
        yield c.emit('test_set_data', ['light', 'red'])
        yield c.read()
        self.assertEqual({'light': 'red'}, c.data)
        yield c.close()

    @tornado.testing.gen_test
    def test_data_with_data_cb(self):
        c = yield self.connect(self.analysis)
        yield c.emit('test_data', ['light2', 'red'])
        yield c.read()
        self.assertEqual({'light2': 'red-modified'}, c.data)
        yield c.close()

    @tornado.testing.gen_test
    def test_class_data(self):
        c = yield self.connect(self.analysis)
        yield c.emit('test_class_data', ['light', 'red'])
        yield c.read()
        self.assertEqual({'light': 'red'}, c.class_data)
        yield c.close()

    @tornado.testing.gen_test
    def test_class_data_with_data_cb(self):
        c = yield self.connect(self.analysis)
        yield c.emit('test_class_data', ['light2', 'red'])
        yield c.read()
        self.assertEqual({'light2': 'red-modified'}, c.class_data)
        yield c.close()


class Parameters(ParametersTestCases, ConnectionTestCase):
    analyses_path = 'databench.tests.analyses'
    analysis = 'parameters'


class ParametersPy(ParametersTestCases, ConnectionTestCase):
    analyses_path = 'databench.tests.analyses'
    analysis = 'parameters_py'
