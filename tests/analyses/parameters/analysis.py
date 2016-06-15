import databench


class Parameters(databench.Analysis):

    def on_test_fn(self, first_param, second_param=100):
        """Echo params."""
        self.emit('test_fn', (first_param, second_param))

    def on_test_action(self):
        """process an action without a message"""
        self.emit('test_action_ack')
