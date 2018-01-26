import databench


class Parameters(databench.Analysis):

    @databench.on
    def test_fn(self, first_param, second_param=100):
        """Echo params."""
        yield self.emit('test_fn', (first_param, second_param))

    @databench.on
    def test_action(self):
        """process an action without a message"""
        yield self.emit('test_action_ack')

    @databench.on
    def test_state(self, key, value):
        """Store some test data."""
        yield self.set_state({key: value})

    @databench.on
    def test_set_data(self, key, value):
        """Store some test data."""
        yield self.data.set(key, value)

    @databench.on
    def test_class_data(self, key, value):
        """Store key-value in class data."""
        yield self.class_data.set(key, value)
