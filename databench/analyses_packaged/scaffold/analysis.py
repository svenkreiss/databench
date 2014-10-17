"""Scaffold analysis. Just a placeholder."""

import databench

import time
import datetime


class Analysis(databench.Analysis):

    def on_connect(self):
        """Run as soon as a browser connects to this.

        CHANGEME
        """
        self.emit('log', 'backend is connected and initialized')
        time.sleep(3)
        self.emit('ready', 'ready at ' +
                  datetime.datetime.now().isoformat())

    def on_got_ready_signal(self, msg):
        """This is the signal the frontend sends back to the backend once
        it received the 'ready' signal from the on_connect() function.

        CHANGEME
        """

        time.sleep(3)
        self.emit('log', 'Backend received the confirmation from the frontend '
                  'that the ready signal was received.')


META = databench.Meta('scaffold', __name__, __doc__, Analysis)
