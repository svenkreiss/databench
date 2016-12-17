import databench_py
import databench_py.singlethread


class Scaffold_Py(databench_py.Analysis):

    def on_connect(self):
        """Run as soon as a browser connects to this."""
        self.data['status'] = 'Hello World'


if __name__ == '__main__':
    analysis = databench_py.singlethread.Meta('scaffold_py', Scaffold_Py)
    analysis.event_loop()
