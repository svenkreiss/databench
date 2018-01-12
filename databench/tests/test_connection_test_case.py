import databench
from databench.testing import ConnectionTestCase
from tornado.testing import gen_test


class Echo(databench.Analysis):
    @databench.on
    def test_data(self, key, value):
        yield self.emit(key, value)


class ExampleTest(ConnectionTestCase):
    def get_app(self):
        return databench.app.SingleApp(Echo).tornado_app()

    @gen_test
    def test_data(self):
        c = yield self.connect()
        yield c.emit('test_data', ['light', 'red'])
        yield c.read()
        yield c.close()

        self.assertEqual(['red'], c.messages['light'])
