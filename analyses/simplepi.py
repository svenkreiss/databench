import math
from time import sleep
from random import random

import databench


signals = databench.Signals('simplepi')

@signals.on('connect')
def calc():
	inside = 0
	for i in range(10000):
		sleep(0.001)
		r1, r2 = (random(), random())
		if r1*r1 + r2*r2 < 1.0: inside += 1

		if (i+1)%100 == 0:
			draws = i+1
			signals.emit('log', {'draws':draws, 'inside':inside, 'r1':r1, 'r2':r2})

			uncertainty = 4.0*math.sqrt(draws*inside/draws*(1.0 - inside/draws)) / draws
			signals.emit('status', {'pi-estimate': 4.0*inside/draws, 'pi-uncertainty': uncertainty})

	signals.emit('log', {'action':'done'})


simplepi = databench.Analysis('simplepi', __name__, signals)
simplepi.description = "Calculating \(\pi\) the simple way."
