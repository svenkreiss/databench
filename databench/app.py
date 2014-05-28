from gevent import monkey
monkey.patch_all()

import os

from flask import Flask, render_template, send_from_directory
from flask.ext.socketio import SocketIO, emit


flaskapp = Flask(__name__)
flaskapp.config['SECRET_KEY'] = 'secret!'
flaskapp.debug = True

import analyses
from databench.analysis import listAll as allAnalyses
for a in allAnalyses:
	print('Registering analysis '+a.name+' as blueprint in flask.')
	flaskapp.register_blueprint(a.blueprint, url_prefix='/'+a.name)

socketio = SocketIO(flaskapp)
for a in allAnalyses:
	print('Connecting socket.io to '+a.name+'.')
	a.signals.setSocketIO(socketio)


@flaskapp.route('/')
def index():
	return render_template(
		'index.html', 
		analyses=allAnalyses
	)


def run():
	socketio.run(flaskapp)
	

if __name__ == '__main__':
	run()

