from gevent import monkey
monkey.patch_all()

import os

from flask import Flask, render_template, send_from_directory
from flask.ext.socketio import SocketIO, emit


flaskapp = Flask(__name__)
flaskapp.config['SECRET_KEY'] = 'secret!'
flaskapp.debug = True
try:
	import analyses
	for bp in analyses.blueprints:
		print('Registering blueprint '+bp.name+'.')
		flaskapp.register_blueprint(bp, url_prefix='/'+bp.name)
except:
	raise RuntimeError("Did not find analyses.")
socketio = SocketIO(flaskapp)
analyses.wire_signals(socketio)


@flaskapp.route('/')
def index():
	return render_template(
		'index.html', 
		analyses=[bp.name for bp in analyses.blueprints]
	)


def run():
	socketio.run(flaskapp)
	

if __name__ == '__main__':
	run()

