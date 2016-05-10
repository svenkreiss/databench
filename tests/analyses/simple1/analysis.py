import databench
import datetime


class Simple1(databench.Analysis):

    def on_connect(self):
        """Run as soon as a browser connects to this."""
        formatted_time = datetime.datetime.now().isoformat()
        self.data['status'] = 'ready since {}'.format(formatted_time)

    def on_ack(self, msg):
        """process 'ack' action"""
        self.data['status'] = 'acknowledged'

    def on_test_fn(self, first_param, second_param=100):
        """Echo params."""
        print(first_param, second_param)
        self.emit('test_fn', {
            'first_param': first_param,
            'second_param': second_param,
        })


META = databench.Meta('simple1', Simple1)
