import databench


class Scaffold(databench.Analysis):

    def on_connected(self):
        """Run as soon as a browser connects to this."""
        self.data['status'] = 'Hello World'
