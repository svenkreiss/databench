from __future__ import division

import databench
import math
import random


class Dummypi(databench.Analysis):
    """A dummy analysis."""

    @databench.on
    def connected(self):
        yield self.data.init({'samples': 100000})

    @databench.on
    def run(self):
        """Run when button is pressed."""

        inside = 0
        for draws in range(1, self.data['samples']):
            # generate points and check whether they are inside the unit circle
            r1 = random.random()
            r2 = random.random()
            if r1 ** 2 + r2 ** 2 < 1.0:
                inside += 1

            # every 1000 iterations, update status
            if draws % 1000 != 0:
                continue

            # debug
            yield self.emit('log', {'draws': draws, 'inside': inside})

            # calculate pi and its uncertainty given the current draws
            p = inside / draws
            pi = {
                'estimate': 4.0 * p,
                'uncertainty': 4.0 * math.sqrt(draws * p * (1.0 - p)) / draws,
            }

            # send status to frontend
            yield self.set_state(pi=pi)

        yield self.emit('log', {'action': 'done'})

    @databench.on
    def samples(self, value):
        yield self.set_state(samples=value)
