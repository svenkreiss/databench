import math
from time import sleep
from random import random

from redis import Redis
from rq import Queue
q = Queue(connection=Redis())

import databench

def inside(job, draws=100):
	inside = 0
	for i in range(draws):
		sleep(0.001)
		r1, r2 = (random(), random())
		if r1*r1 + r2*r2 < 1.0: inside += 1
	return (job, inside, draws)


signals = databench.Signals('slowpi')

@signals.on('connect')
def calc():
	jobs = []
	for i in range(100):
		jobs.append(q.enqueue(inside, i))
		signals.emit('log', {'enqueued_job': i})
	
	drawsCount = 0
	insideCount = 0
	while jobs:
		newJobList = []
		for j in jobs:
			if j.result:
				drawsCount += j.result[2]
				insideCount += j.result[1]
				signals.emit('log', {'result': j.result, 'draws':drawsCount, 'inside':insideCount})

				uncertainty = 4.0*math.sqrt(drawsCount*insideCount/drawsCount*(1.0 - insideCount/drawsCount)) / drawsCount
				signals.emit('status', {'pi-estimate': 4.0*insideCount/drawsCount, 'pi-uncertainty': uncertainty})
			else:
				newJobList.append(j)
		jobs = newJobList
		sleep(0.1)
	signals.emit('log', {'action':'done'})


slowpi = databench.Analysis('slowpi', __name__, signals)
slowpi.description = "Calculating \(\pi\) the redis-queue way ... yes, in parallel."

