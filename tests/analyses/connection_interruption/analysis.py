import databench


class ConnectionInterruption(databench.Analysis):

    def on_connect(self):
        self.data['count'] = 0

    def on_state(self, state):
        self.data['state'] = state
        self.data['count'] += 1
