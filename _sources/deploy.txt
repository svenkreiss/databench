
Deployment
----------

The standard use case is to run ``databench`` locally. However, Databench can also be deployed on servers/platforms that support deploying Flask and WebSockets. 


Heroku
++++++

You need a ``Procfile`` file

.. code-block:: bash

	web: databench

and a ``requirements.txt`` file

.. code-block:: python

	Flask==0.10.1
	Flask-SocketIO==0.3.7
	Jinja2==2.7.2
	MarkupSafe==0.23
	Werkzeug==0.9.4
	gevent==1.0.1
	gevent-socketio==0.3.6
	gevent-websocket==0.9.3
	greenlet==0.4.2
	itsdangerous==0.24
	matplotlib==1.3.1
	mpld3==0.2
	wsgiref==0.1.2

	git+https://github.com/svenkreiss/databench.git

which already includes the most common dependencies. Databench will pick up the environment variable ``PORT`` which will be used for Flask.

Currently, WebSockets are still a Heroku labs feature. It is enabled with

.. code-block:: bash

	$ heroku labs:enable websockets

An example repository that is deployed on Heroku is `databench_examples_viewer`_.

.. _`databench_examples_viewer`: https://github.com/svenkreiss/databench_examples_viewer
