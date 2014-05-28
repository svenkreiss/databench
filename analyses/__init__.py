import slowpi

blueprints = [slowpi.slowpi]

def wire_signals(socketio):
	slowpi.wire_signals(socketio)
