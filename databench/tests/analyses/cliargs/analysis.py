import databench


class CliArgs(databench.Analysis):

    def on_connected(self):
        """Run as soon as a browser connects to this."""
        self.data['cli_args'] = self.cli_args
