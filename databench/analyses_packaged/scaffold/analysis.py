import databench


class Scaffold(databench.Analysis):

    @databench.on
    def connected(self):
        """Run as soon as a browser connects to this."""
        yield self.data.init(status='Hello World')
