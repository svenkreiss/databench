"""Executable for Databench."""

from gevent import monkey

import os
import sys

from flask import Flask, render_template, url_for
from flask.ext.socketio import SocketIO
from flask.ext.markdown import Markdown

import codecs
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
    flaskapp.debug = True
    flaskapp.config['SECRET_KEY'] = 'ajksdfjhkasdfj' # change

    # add read_file capability
    flaskapp.jinja_env.globals['read_file'] = lambda filename: \
        codecs.open(os.getcwd()+'/analyses/'+filename, 'r', 'utf-8').readlines()

    # add markdown jinja extension
    markdown = Markdown(flaskapp, extensions=['fenced_code'])


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
        a.signals._set_socket_io(socketio)

    @flaskapp.route('/')
    def index():
        print url_for('static', filename='dummypi.png')
        return render_template(
            'index.html',
            analyses=allAnalyses
        )

    return (flaskapp, socketio)

def run():
    monkey.patch_all()
    flaskapp, socketio = init_app()
    port = int(os.environ.get('PORT', 5000))
    socketio.run(flaskapp, host='0.0.0.0', port=port)


if __name__ == '__main__':
    run()

