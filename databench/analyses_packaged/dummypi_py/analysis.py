from __future__ import division

import math
from random import random
from time import sleep

import databench_py
import databench_py.singlethread

import logging
logging.basicConfig(level='DEBUG')


class Dummypi_Py(databench_py.Analysis):

    def on_connected(self):
        self.data['samples'] = 1000

    def on_run(self):
        """Run when button is pressed."""

        inside = 0
        for i in range(self.data['samples']):
            sleep(0.001)
            r1, r2 = (random(), random())
            if r1 ** 2 + r2 ** 2 < 1.0:
                inside += 1

            if (i + 1) % 100 == 0:
                draws = i + 1
                self.emit('log', {
                    'draws': draws,
                    'inside': inside,
                    'r1': r1,
                    'r2': r2,
                })

                p = inside / draws
                uncertainty = 4.0 * math.sqrt(draws * p * (1.0 - p)) / draws
                self.data['pi'] = {
                    'estimate': 4.0 * inside / draws,
                    'uncertainty': uncertainty,
                }

        self.emit('log', {'action': 'done'})


if __name__ == "__main__":
    analysis = databench_py.singlethread.Meta('dummypi_py', Dummypi_Py)
    analysis.event_loop()
