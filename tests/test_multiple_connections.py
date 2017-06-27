import databench
from databench.testing import AnalysisTestCase, gen_test

databench.meta.PING_INTERVAL = 500


class MultipleConnections(object):

    @gen_test
    def test_run(self):
        connections = []

        for _ in range(4):
            connection = yield self.connect(self.analysis)
            connections.append(connection)

        for connection in connections:
            self.assertEqual(len(connection.analysis_id), 8)

        for connection in connections:
            yield connection.close()


class MultipleDummypi(MultipleConnections, AnalysisTestCase):
    analysis = 'dummypi'


class MultipleDummypiPy(MultipleConnections, AnalysisTestCase):
    analysis = 'dummypi_py'
