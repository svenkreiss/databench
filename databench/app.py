import os

from flask import Flask, render_template, send_from_directory
from flask.ext.socketio import SocketIO, emit


flaskapp = Flask(__name__)
flaskapp.debug = True
try:
	import backend
	for bp in backend.blueprints:
		print('Registering blueprint '+bp.name+'.')
		flaskapp.register_blueprint(bp, url_prefix='/'+bp.name)
except:
	raise("Did not find backend.")
socketio = SocketIO(flaskapp)


@flaskapp.route('/')
def index():
	return render_template(
		'index.html', 
		analyses=[bp.name for bp in backend.blueprints]
	)


@socketio.on('my event')
def test_message(message):
	emit('my response', {'data': 'got it!'})


def run():
	socketio.run(flaskapp)
	

if __name__ == '__main__':
	run()

