import databench


class RequestArgs(databench.Analysis):

    def on_connected(self):
        """Echo params."""
        self.emit('ack', self.request_args)
