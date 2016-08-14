import databench


class ConnectionInterruption(databench.Analysis):

    def __init__(self, analysis_id=None):
        super(ConnectionInterruption, self).__init__(analysis_id)
        if analysis_id is None:
            self.data['count'] = 0

    def on_state(self, state):
        self.data['state'] = state
        self.data['count'] += 1
