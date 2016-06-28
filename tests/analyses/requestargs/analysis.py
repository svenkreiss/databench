import databench


class RequestArgs(databench.Analysis):

    def on_request_args(self, argv):
        """Echo params."""
        self.emit('ack', argv)
