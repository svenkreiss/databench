from flask import Blueprint, render_template
from flask.ext.socketio import emit


myanalysis = Blueprint(
	'myanalysis', 
	__name__,
	template_folder='templates'
)


@myanalysis.route('/')
def index():
	return render_template('overview.html')


def wire_signals(socketio):

	@socketio.on('my event', namespace='/myanalysis')
	def myanalysis_message(message):
		print('my event')
		emit('my response', {'data': 'got it!'})

	@socketio.on('connect', namespace='/myanalysis')
	def myanalysis_connect():
		print('connect')
		emit('my response', {'data': 'Connected', 'count': 0})

	@socketio.on('disconnect', namespace='/myanalysis')
	def myanalysis_disconnect():
		print('Client disconnected')
