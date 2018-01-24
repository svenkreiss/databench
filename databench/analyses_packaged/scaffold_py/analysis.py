import databench
import databench_py.singlethread


class Scaffold_Py(databench.Analysis):

    @databench.on
    def connected(self):
        """Run as soon as a browser connects to this."""
        yield self.set_state(status='Hello World')


if __name__ == '__main__':
    analysis = databench_py.singlethread.Meta('scaffold_py', Scaffold_Py)
    analysis.event_loop()
