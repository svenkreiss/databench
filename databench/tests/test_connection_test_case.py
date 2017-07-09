from databench.testing import ConnectionTestCase
from tornado.testing import gen_test


class Example(ConnectionTestCase):
    analyses_path = 'databench.tests.analyses'

    @gen_test
    def test_data(self):
        c = yield self.connect('parameters')
        yield c.emit('test_data', ['light', 'red'])
        yield c.read()
        self.assertEqual({'light': 'red'}, c.data)
        yield c.close()
