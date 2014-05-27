import os

from flask import Flask, render_template, send_from_directory
from flask.ext.socketio import SocketIO, emit


flaskapp = Flask(__name__)
flaskapp.config['SECRET_KEY'] = 'secret'
flaskapp.debug = True
socketio = SocketIO(flaskapp)


@flaskapp.route('/')
def index():
	return render_template('index.html')


@socketio.on('my event')
def test_message(message):
	emit('my response', {'data': 'got it!'})


def run():
	socketio.run(flaskapp)
	

if __name__ == '__main__':
	run()

