from flask.ext.socketio import emit

class Signals:
	def __init__(self, namespace):
		self.signalCache = []
		self.socketio = None
		self.namespace = namespace

	def on(self, signal):
		""" This is a decorator with an argument without a wrapper. """

		def decorator(callback):
			if not self.socketio:
				self.signalCache.append( (signal,callback) )
			else:
				@self.socketio.on(signal, namespace='/'+self.namespace)
				def dummy():
					callback()

		return decorator

	def setSocketIO(self, socketio):
		self.socketio = socketio
		for sc in self.signalCache:
			@self.socketio.on(sc[0], namespace='/'+self.namespace)
			def dummy():
				sc[1]()
		self.signalCache = []

	def emit(self, signal, message):
		emit(signal, message)
