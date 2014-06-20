"""Executable for Databench."""

from gevent import monkey

import os
import sys

from flask import Flask, render_template
from flask.ext.socketio import SocketIO
from flask.ext.markdown import Markdown

import codecs

from databench import __version__ as DATABENCH_VERSION
from databench.analysis import LIST_ALL as LIST_ALL_ANALYSES


class App(object):
    """Similar to a flask.Flask app. The actual Flask instance is injected.

    Args:
        name (str): Name of the app.
        host (str): Host name.
        port (int): Port number.
        flask_app (flask.Flask, optional): An instance of flask.Flask.

    """

    def __init__(self, import_name, host='0.0.0.0', port=5000, flask_app=None):

        if flask_app == None:
            self.flask_app = Flask(import_name)
        else:
            self.flask_app = flask_app

        self.host = host
        self.port = port

        self.socketio = None
        self.description = None
        self.analyses_author = None
        self.analyses_version = None

        self.flask_app.debug = True
        self.flask_app.config['SECRET_KEY'] = 'ajksdfjhkasdfj' # change

        self.add_jinja2_highlight()
        self.add_read_file()
        self.add_markdown()
        self.import_analyses()
        self.register_analyses()

        self.flask_app.add_url_rule('/', 'render_index', self.render_index)


    def run(self):
        """Entry point to run the app."""
        self.socketio.run(self.flask_app, host=self.host, port=self.port)

    def add_jinja2_highlight(self):
        """Add jinja2 highlighting."""
        self.flask_app.jinja_options['extensions'].append(
            'jinja2_highlight.HighlightExtension'
        )

    def add_read_file(self):
        """Add read_file capability."""
        self.flask_app.jinja_env.globals['read_file'] = lambda filename: \
            codecs.open(
                os.getcwd()+'/analyses/'+filename,
                'r',
                'utf-8'
            ).readlines()

    def add_markdown(self):
        """Add Markdown capability."""
        Markdown(self.flask_app, extensions=['fenced_code'])

    def import_analyses(self):
        """Add analyses from the analyses folder."""

        sys.path.append('.')
        try:
            import analyses
            self.description = analyses.__doc__
            try:
                self.analyses_author = analyses.__author__
            except AttributeError:
                print 'Analyses module does not have an author string.'
            try:
                self.analyses_version = analyses.__version__
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
            self.description = analyses_packaged.__doc__
            try:
                self.analyses_author = analyses_packaged.__author__
            except AttributeError:
                print 'Analyses module does not have an author string.'
            try:
                self.analyses_version = analyses_packaged.__version__
            except AttributeError:
                print 'Analyses module does not have a version string.'

    def register_analyses(self):
        """Register analyses (analyses need to be imported first)."""

        for analysis in LIST_ALL_ANALYSES:
            print 'Registering analysis '+analysis.name+' as blueprint ' \
                  'in flask.'
            self.flask_app.register_blueprint(
                analysis.blueprint,
                url_prefix='/'+analysis.name
            )

        self.socketio = SocketIO(self.flask_app)
        for analysis in LIST_ALL_ANALYSES:
            print 'Connecting socket.io to '+analysis.name+'.'
            analysis.signals.set_socket_io(self.socketio)

    def render_index(self):
        """Render the List-of-Analyses overview page."""
        return render_template(
            'index.html',
            analyses=LIST_ALL_ANALYSES,
            analyses_author=self.analyses_author,
            analyses_version=self.analyses_version,
            description=self.description,
            databench_version=DATABENCH_VERSION
        )


def run():
    """Entry point to run databench."""
    monkey.patch_all()
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app = App(__name__, host=host, port=port)
    app.run()


if __name__ == '__main__':
    run()

