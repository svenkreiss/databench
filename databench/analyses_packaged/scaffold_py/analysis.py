import time
import datetime

import databench_py
import databench_py.singlethread


class Analysis(databench_py.Analysis):

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


if __name__ == "__main__":
    analysis = databench_py.singlethread.Meta('scaffold_py', Analysis)
    analysis.event_loop()
