from __future__ import division

import math
from random import random

import databench
import databench_py.singlethread

import logging
logging.basicConfig(level='DEBUG')


class Dummypi_Py(databench.Analysis):
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
            r1, r2 = (random(), random())
            if r1 ** 2 + r2 ** 2 < 1.0:
                inside += 1

            if draws % 1000 != 0:
                continue

            # debug
            yield self.emit('log', {'draws': draws, 'inside': inside})

            # calculate pi and its uncertainty given the current draws
            p = inside / draws
            pi = {
                'estimate': 4.0 * inside / draws,
                'uncertainty': 4.0 * math.sqrt(draws * p * (1.0 - p)) / draws,
            }

            # send status to frontend
            yield self.set_state(pi=pi)

        yield self.emit('log', {'action': 'done'})


if __name__ == "__main__":
    analysis = databench_py.singlethread.Meta('dummypi_py', Dummypi_Py)
    analysis.event_loop()
