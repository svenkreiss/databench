import databench
from databench.testing import AnalysisTestCase
import tornado.testing

databench.meta.PING_INTERVAL = 500


class MultipleConnections(object):

    @tornado.testing.gen_test
    def test_run(self):
        connections = []

        for _ in range(4):
            connection = self.connection(self.analysis)
            yield connection.connect()
            connections.append(connection)

        for connection in connections:
            self.assertEqual(len(connection.analysis_id), 8)

        for connection in connections:
            yield connection.close()


class MultipleDummypi(MultipleConnections, AnalysisTestCase):
    analysis = 'dummypi'


class MultipleDummypiPy(MultipleConnections, AnalysisTestCase):
    analysis = 'dummypi_py'
