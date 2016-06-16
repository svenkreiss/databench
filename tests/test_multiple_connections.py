import databench
import tornado.testing


class MultipleConnections(object):

    @tornado.testing.gen_test
    def test_run(self):
        connections = []

        for _ in range(4):
            connection = yield self.ws_connect(self.analysis)
            connections.append(connection)

        for connection in connections:
            self.assertEqual(len(connection.analysis_id), 8)

        for connection in connections:
            yield connection.close()


class MultipleDummypi(MultipleConnections, databench.AnalysisTestCase):
    analysis = 'dummypi'


class MultipleDummypiPy(MultipleConnections, databench.AnalysisTestCase):
    analysis = 'dummypi_py'
