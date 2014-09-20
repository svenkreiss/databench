"""Scaffold analysis. Just a placeholder."""

import databench_py
import databench_py.singlethread


class Analysis(databench_py.Analysis):

    def on_connect(self):
        """Run as soon as a browser connects to this."""
        self.emit('log', {'action': 'done'})


if __name__ == "__main__":
    analysis = databench_py.singlethread.Meta(
        'scaffold_py', __name__, __doc__, Analysis
    )
    analysis.event_loop()
