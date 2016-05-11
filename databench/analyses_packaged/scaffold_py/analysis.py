import datetime
import time

import databench_py
import databench_py.singlethread


class Scaffold_Py(databench_py.Analysis):

    def on_connect(self):
        """Run as soon as a browser connects to this."""
        time.sleep(1)
        formatted_time = datetime.datetime.now().isoformat()
        self.data['status'] = 'ready since {}'.format(formatted_time)

    def on_ack(self, msg):
        """process 'ack' action"""
        time.sleep(1)
        self.data['status'] = 'acknowledged'


if __name__ == "__main__":
    analysis = databench_py.singlethread.Meta('scaffold_py', Scaffold_Py)
    analysis.event_loop()
