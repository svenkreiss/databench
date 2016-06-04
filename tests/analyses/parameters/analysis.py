import databench


class Parameters(databench.Analysis):

    def on_test_fn(self, first_param, second_param=100):
        """Echo params."""
        print(first_param, second_param)
        self.emit('test_fn', (first_param, second_param))
