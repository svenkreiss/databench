from gevent import monkey
monkey.patch_all()

import os
import sys

from flask import Flask, render_template, send_from_directory
from flask.ext.socketio import SocketIO, emit
import jinja2_highlight

class MyFlask(Flask):
	jinja_options = dict(Flask.jinja_options)
	jinja_options.setdefault(
		'extensions',
		[]
	).append('jinja2_highlight.HighlightExtension')


flaskapp = MyFlask(__name__)
flaskapp.config['SECRET_KEY'] = 'secret!'
flaskapp.debug = True


sys.path.append('.')
try:
	import analyses
except ImportError:
	print("Did not find 'analyses' module.")
	print("--- debug - sys.path: "+str(sys.path))
	print("--- debug - os.path.dirname(os.path.realpath(__file__): "+os.path.dirname(os.path.realpath(__file__)))
	print("--- debug - os.getcwd: "+os.getcwd())

	print("Using packaged analyses.")
	import analyses_packaged
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
	port = int(os.environ.get('PORT', 5000))
	socketio.run(flaskapp, host='0.0.0.0', port=port)
	

if __name__ == '__main__':
	run()

