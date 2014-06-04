"""Executable for Databench."""

from gevent import monkey
monkey.patch_all()

import os
import sys

from flask import Flask, render_template, url_for
from flask.ext.socketio import SocketIO

import jinja2_highlight
from jinja2 import Markup


class MyFlask(Flask):
    """Wrapper for Flask to enable jinja2_highlight."""
    jinja_options = dict(Flask.jinja_options)
    jinja_options.setdefault(
        'extensions',
        []
    ).append('jinja2_highlight.HighlightExtension')


def init_app():
    """Initialize Flask app."""

    flaskapp = MyFlask(__name__)
    flaskapp.jinja_env.globals['include_raw'] = lambda filename: \
        Markup(
            flaskapp.jinja_loader.get_source(flaskapp.jinja_env, filename)[0]
        )
    flaskapp.config['SECRET_KEY'] = 'secret!'
    flaskapp.debug = True


    sys.path.append('.')
    try:
        import analyses
    except ImportError:
        print "Did not find 'analyses' module."
        print "--- debug - sys.path: "+str(sys.path)
        print "--- debug - os.path.dirname(os.path.realpath(__file__): "+os.path.dirname(os.path.realpath(__file__))
        print "--- debug - os.getcwd: "+os.getcwd()

        print "Using packaged analyses."
        import analyses_packaged
    from databench.analysis import LIST_ALL as allAnalyses
    for a in allAnalyses:
        print 'Registering analysis '+a.name+' as blueprint in flask.'
        flaskapp.register_blueprint(a.blueprint, url_prefix='/'+a.name)

    socketio = SocketIO(flaskapp)
    for a in allAnalyses:
        print 'Connecting socket.io to '+a.name+'.'
        a.signals.setSocketIO(socketio)

    @flaskapp.route('/')
    def index():
        print url_for('static', filename='dummypi.png')
        return render_template(
            'index.html',
            analyses=allAnalyses
        )

    return flaskapp

def run():
    flaskapp = init_app()
    port = int(os.environ.get('PORT', 5000))
    socketio.run(flaskapp, host='0.0.0.0', port=port)


if __name__ == '__main__':
    run()

