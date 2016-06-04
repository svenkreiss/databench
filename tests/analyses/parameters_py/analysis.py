import databench_py
import databench_py.singlethread


class Parameters_Py(databench_py.Analysis):

    def on_test_fn(self, first_param, second_param=100):
        """Echo params."""
        self.emit('test_fn', (first_param, second_param))


if __name__ == "__main__":
    analysis = databench_py.singlethread.Meta('parameters_py', Parameters_Py)
    analysis.event_loop()
