import datetime
import time

import databench


class Simple2(databench.Analysis):

    def on_connect(self):
        """Run as soon as a browser connects to this."""
        time.sleep(1)
        formatted_time = datetime.datetime.now().isoformat()
        self.data['status'] = 'ready since {}'.format(formatted_time)

    def on_ack(self, msg):
        """process 'ack' action"""

        time.sleep(1)
        self.data['status'] = 'acknowledged'


META = databench.Meta('simple2', Simple2)
