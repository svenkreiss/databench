import datetime
import time

import databench_py
import databench_py.singlethread


class Simple1_Py(databench_py.Analysis):

    def on_connect(self):
        """Run as soon as a browser connects to this."""
        time.sleep(1)
        formatted_time = datetime.datetime.now().isoformat()
        self.data['status'] = 'ready since {}'.format(formatted_time)

    def on_ack(self, msg):
        """process 'ack' action"""

        time.sleep(1)
        self.data['status'] = 'acknowledged'

    def on_test_fn(self, first_param, second_param=100):
        """Echo params."""
        self.emit('test_fn', {
            'first_param': first_param,
            'second_param': second_param,
        })


if __name__ == "__main__":
    analysis = databench_py.singlethread.Meta('simple1_py', Simple1_Py)
    analysis.event_loop()
