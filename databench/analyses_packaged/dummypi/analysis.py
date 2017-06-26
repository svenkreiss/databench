from __future__ import division

import math
import random
import tornado.gen

import databench


class Dummypi(databench.Analysis):

    def on_connected(self):
        self.data['samples'] = 1000

    @tornado.gen.coroutine
    def on_run(self):
        """Run when button is pressed."""

        inside = 0
        for draws in range(1, self.data['samples']):
            yield tornado.gen.sleep(0.001)

            # generate points and check whether they are inside the unit circle
            r1 = random.random()
            r2 = random.random()
            if r1 ** 2 + r2 ** 2 < 1.0:
                inside += 1

            # every 100 iterations, update status
            if draws % 100 != 0:
                continue

            # debug
            self.emit('log', {'draws': draws, 'inside': inside})

            # calculate pi and its uncertainty given the current draws
            pi = 4.0 * inside / draws
            p = inside / draws
            uncertainty = 4.0 * math.sqrt(draws * p * (1.0 - p)) / draws

            # send status to frontend
            self.data['pi'] = {'estimate': pi, 'uncertainty': uncertainty}

        self.emit('log', {'action': 'done'})
