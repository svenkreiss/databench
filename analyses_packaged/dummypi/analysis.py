"""Calculating \\(\\pi\\) the simple way, but this is called
dummypi to avoid conflict with simplepi in the databench_examples repo."""

import math
from time import sleep
from random import random

import databench


class Analysis(databench.Analysis):

    def on_run(self):
        """Run as soon as a browser connects to this."""

        inside = 0
        for i in range(10000):
            sleep(0.001)
            r1, r2 = (random(), random())
            if r1*r1 + r2*r2 < 1.0:
                inside += 1

            if (i+1) % 100 == 0:
                draws = i+1
                self.emit('log', {
                    'draws': draws,
                    'inside': inside,
                    'r1': r1,
                    'r2': r2,
                })

                p = float(inside)/draws
                uncertainty = 4.0*math.sqrt(draws*p*(1.0 - p)) / draws
                self.emit('status', {
                    'pi-estimate': 4.0*inside/draws,
                    'pi-uncertainty': uncertainty
                })

        self.emit('log', {'action': 'done'})


META = databench.Meta('dummypi', __name__, __doc__, Analysis)
