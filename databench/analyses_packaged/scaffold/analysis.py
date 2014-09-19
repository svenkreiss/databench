"""Scaffold analysis. Just a placeholder."""

import databench


class Analysis(databench.Analysis):

    def on_connect(self):
        """Run as soon as a browser connects to this."""
        self.emit('log', {'action': 'done'})


META = databench.Meta('scaffold', __name__, __doc__, Analysis)
