import databench


class CmdArgs(databench.Analysis):

    def on_connect(self):
        """Run as soon as a browser connects to this."""
        self.cmd_args = None

    def on_cmd_args(self, args):
        self.data['cmd_args'] = args
