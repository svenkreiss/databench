import databench
import tornado.testing


class Yodler(databench.Analysis):
    """A simple analysis that we want to test."""

    @databench.on
    def echo(self, key, value):
        """An action that applies the given key and value to the state."""
        yield self.set_state({key: value})


class Example(tornado.testing.AsyncTestCase):
    """Test cases for the Yodler analysis."""

    @tornado.testing.gen_test
    def test_gentest(self):
        """Demonstrating the decorator pattern for tests."""
        test = databench.testing.AnalysisTest(Yodler)
        yield test.trigger('echo', ['light', 'red'])
        self.assertIn(('data', {'light': 'red'}), test.emitted_messages)

    def test_stopwait(self):
        """Demonstrating the stop-wait-callback pattern for tests."""
        test = databench.testing.AnalysisTest(Yodler)
        test.trigger('echo', ['light', 'red'], callback=self.stop)
        self.wait()
        self.assertIn(('data', {'light': 'red'}), test.emitted_messages)
