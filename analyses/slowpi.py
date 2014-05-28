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


from time import sleep
from random import random

def wire_signals(socketio):

	@socketio.on('connect', namespace='/slowpi')
	def connect():
		print('connect')
		emit('log', {'data': 'Connected', 'count': 0})

	@socketio.on('disconnect', namespace='/slowpi')
	def disconnect():
		print('Client disconnected')

	@socketio.on('start', namespace='/slowpi')
	def message(message):
		print('start')
		emit('log', {'data': message['data']})

		inside = 0
		for i in range(10000):
			sleep(0.001)
			r1 = random()
			r2 = random()
			if r1*r1 + r2*r2 < 1.0: inside += 1

			if (i+1)%100 == 0:
				draws = i+1
				emit('status', {'draws':draws, 'inside':inside, 'r1':r1, 'r2':r2, 'pi-estimate': 4.0*inside/draws})

		emit('log', {'action':'done'})

