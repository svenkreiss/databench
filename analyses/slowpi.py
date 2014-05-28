from flask import Blueprint, render_template
from flask.ext.socketio import emit


slowpi = Blueprint(
	'slowpi', 
	__name__,
	template_folder='templates'
)

@slowpi.route('/')
def index():
	return render_template('slowpi.html')


import math
from time import sleep
from random import random

def wire_signals(socketio):

	@socketio.on('connect', namespace='/slowpi')
	def connect():
		inside = 0
		for i in range(10000):
			sleep(0.001)
			r1, r2 = (random(), random())
			if r1*r1 + r2*r2 < 1.0: inside += 1

			if (i+1)%100 == 0:
				draws = i+1
				emit('log', {'draws':draws, 'inside':inside, 'r1':r1, 'r2':r2})

				uncertainty = 4.0*math.sqrt(draws*inside/draws*(1.0 - inside/draws)) / draws
				emit('status', {'pi-estimate': 4.0*inside/draws, 'pi-uncertainty': uncertainty})

		emit('log', {'action':'done'})
