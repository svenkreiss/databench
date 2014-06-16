"""Executable for Databench."""

from gevent import monkey

import os
import sys

from flask import Flask, render_template
from flask.ext.socketio import SocketIO
from flask.ext.markdown import Markdown

import codecs

from databench import __version__ as databench_version


def init_app():
    """Initialize Flask app."""

    flaskapp = Flask(__name__)
    flaskapp.debug = True
    flaskapp.config['SECRET_KEY'] = 'ajksdfjhkasdfj' # change

    # jinja2_highlight
    flaskapp.jinja_options['extensions'].append(
        'jinja2_highlight.HighlightExtension'
    )

    # add read_file capability
    flaskapp.jinja_env.globals['read_file'] = lambda filename: \
        codecs.open(os.getcwd()+'/analyses/'+filename, 'r', 'utf-8').readlines()

    # add markdown jinja extension
    Markdown(flaskapp, extensions=['fenced_code'])


    sys.path.append('.')
    description = None
    analyses_author = None
    analyses_version = None
    try:
        import analyses
        description = analyses.__doc__
        try:
            analyses_author = analyses.__author__
        except AttributeError:
            print 'Analyses module does not have an author string.'
        try:
            analyses_version = analyses.__version__
        except AttributeError:
            print 'Analyses module does not have a version string.'
    except ImportError:
        print "Did not find 'analyses' module."
        print "--- debug - sys.path: "+str(sys.path)
        print "--- debug - os.path.dirname(os.path.realpath(__file__): "+\
              os.path.dirname(os.path.realpath(__file__))
        print "--- debug - os.getcwd: "+os.getcwd()

        print "Using packaged analyses."
        import analyses_packaged
        description = analyses_packaged.__doc__
        try:
            analyses_author = analyses_packaged.__author__
        except AttributeError:
            print 'Analyses module does not have an author string.'
        try:
            analyses_version = analyses_packaged.__version__
        except AttributeError:
            print 'Analyses module does not have a version string.'
    from databench.analysis import LIST_ALL as LIST_ALL_ANALYSES
    for a in LIST_ALL_ANALYSES:
        print 'Registering analysis '+a.name+' as blueprint in flask.'
        flaskapp.register_blueprint(a.blueprint, url_prefix='/'+a.name)

    socketio = SocketIO(flaskapp)
    for a in LIST_ALL_ANALYSES:
        print 'Connecting socket.io to '+a.name+'.'
        a.signals.set_socket_io(socketio)

    @flaskapp.route('/')
    def index():
        """Render the List-of-Analyses overview page."""
        return render_template(
            'index.html',
            analyses=LIST_ALL_ANALYSES,
            analyses_author=analyses_author,
            analyses_version=analyses_version,
            description=description,
            databench_version=databench_version
        )

    return (flaskapp, socketio)

def run():
    """Entry point to run databench."""
    monkey.patch_all()
    flaskapp, socketio = init_app()
    port = int(os.environ.get('PORT', 5000))
    socketio.run(flaskapp, host='0.0.0.0', port=port)


if __name__ == '__main__':
    run()

