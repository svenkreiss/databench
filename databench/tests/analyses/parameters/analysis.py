import databench
import tornado.gen


class Parameters(databench.Analysis):

    def on_test_fn(self, first_param, second_param=100):
        """Echo params."""
        self.emit('test_fn', (first_param, second_param))

    def on_test_action(self):
        """process an action without a message"""
        self.emit('test_action_ack')

    def on_test_data(self, key, value):
        """Store some test data."""
        self.data[key] = value

    @tornado.gen.coroutine
    def on_test_set_data(self, key, value):
        """Store some test data."""
        yield self.data.set(key, value)

    def on_test_class_data(self, key, value):
        """Store key-value in class data."""
        self.class_data[key] = value
