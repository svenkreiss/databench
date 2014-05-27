#!/usr/bin/env python

"""
The main databench entry point.
"""


import databench


def main():
	print("--- databench ---")
	databench.run()
	# databench.socketio(databench.flaskapp)

if __name__ == "__main__":
	main()
