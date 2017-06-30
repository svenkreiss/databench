import databench


class RequestArgs(databench.Analysis):

    def on_connected(self):
        """Echo params."""
        self.emit('echo_request_args', self.request_args)
