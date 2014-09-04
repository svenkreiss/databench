"""Main Flask App."""

import os
import sys
import glob
import codecs
import logging
import zmq.green as zmq

import flask_sockets
from gevent import pywsgi
from flask.ext.markdown import Markdown
from flask import Flask, render_template
from geventwebsocket.handler import WebSocketHandler

from .analysis import Meta, MetaZMQ
from . import __version__ as DATABENCH_VERSION


class App(object):
    """Similar to a Flask app. The actual Flask instance is injected.

    Args:
        name (str): Name of the app.
        host (str): Host name.
        port (int): Port number.
        flask_app (flask.Flask, optional): An instance of flask.Flask.
        delimiters (dict): Configuration option for the delimiters used for the
            server-side templates. You can specify strings for
            ``variable_start_string``, ``variable_end_string``,
            ``block_start_string``, ``block_end_string``,
            ``comment_start_string``, ``comment_end_string``.

    """

    def __init__(self, import_name, host='0.0.0.0', port=5000, flask_app=None,
                 delimiters=None):

        if flask_app is None:
            self.flask_app = Flask(import_name)
        else:
            self.flask_app = flask_app

        self.host = host
        self.port = port

        self.sockets = flask_sockets.Sockets(self.flask_app)

        self.description = None
        self.analyses_author = None
        self.analyses_version = None

        self.spawned_analyses = {}

        self.flask_app.debug = True
        self.flask_app.use_reloader = True
        self.flask_app.config['SECRET_KEY'] = 'ajksdfjhkasdfj'  # change

        if delimiters:
            self.custom_delimiters(delimiters)
        self.add_jinja2_highlight()
        self.add_read_file()
        self.add_markdown()

        zmq_publish = zmq.Context().socket(zmq.PUB)
        zmq_publish.bind('tcp://127.0.0.1:'+str(port+3041))
        logging.debug('main publishing to port '+str(port+3041))

        self.register_analyses_py(zmq_publish)
        self.register_analyses_pyspark(zmq_publish)
        self.register_analyses_go(zmq_publish)
        self.import_analyses()
        self.register_analyses()

        self.flask_app.add_url_rule('/', 'render_index', self.render_index)

    def run(self):
        """Entry point to run the app."""
        # self.flask_app.run(host=self.host, port=self.port)
        server = pywsgi.WSGIServer((self.host, self.port),
                                   self.flask_app,
                                   handler_class=WebSocketHandler)
        server.serve_forever()

    def custom_delimiters(self, delimiters):
        """Change the standard jinja2 delimiters to allow those delimiters be
        used by frontend template engines."""
        options = self.flask_app.jinja_options.copy()
        options.update(delimiters)
        self.flask_app.jinja_options = options

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

    def register_analyses_py(self, zmq_publish):
        analysis_folders = glob.glob('analyses/*_py')
        if not analysis_folders:
            analysis_folders = glob.glob('analyses_packaged/*_py')

        for analysis_folder in analysis_folders:
            name = analysis_folder[analysis_folder.find('/')+1:]
            if name[0] in ['.', '_']:
                continue
            logging.debug('creating MetaZMQ for '+name)
            MetaZMQ(name, __name__, "ZMQ Analysis py",
                    ['python', analysis_folder+'/analysis.py'],
                    zmq_publish)

    def register_analyses_pyspark(self, zmq_publish):
        analysis_folders = glob.glob('analyses/*_pyspark')
        if not analysis_folders:
            analysis_folders = glob.glob('analyses_packaged/*_pyspark')

        for analysis_folder in analysis_folders:
            name = analysis_folder[analysis_folder.find('/')+1:]
            if name[0] in ['.', '_']:
                continue
            logging.debug('creating MetaZMQ for '+name)
            MetaZMQ(name, __name__, "ZMQ Analysis py",
                    ['pyspark', analysis_folder+'/analysis.py'],
                    zmq_publish)

    def register_analyses_go(self, zmq_publish):
        analysis_folders = glob.glob('analyses/*_go')
        if not analysis_folders:
            analysis_folders = glob.glob('analyses_packaged/*_go')

        for analysis_folder in analysis_folders:
            name = analysis_folder[analysis_folder.find('/')+1:]
            if name[0] in ['.', '_']:
                continue
            logging.info('installing '+name)
            os.system('cd '+analysis_folder+'; go install')
            logging.debug('creating MetaZMQ for '+name)
            MetaZMQ(name, __name__, "ZMQ Analysis go",
                    [name], zmq_publish)

    def import_analyses(self):
        """Add analyses from the analyses folder."""

        sys.path.append('.')
        try:
            import analyses
            self.description = analyses.__doc__
            try:
                self.analyses_author = analyses.__author__
            except AttributeError:
                logging.info('Analyses module does not have an author string.')
            try:
                self.analyses_version = analyses.__version__
            except AttributeError:
                logging.info('Analyses module does not have a version string.')
        except ImportError, e:
            if str(e) != 'No module named analyses':
                raise e

            print "Did not find 'analyses' module."
            logging.debug('sys.path: '+str(sys.path))
            logging.debug('os.path.dirname(os.path.realpath(__file__)): ' +
                          os.path.dirname(os.path.realpath(__file__)))
            logging.debug('os.getcwd: '+os.getcwd())

            print "Using packaged analyses."
            import analyses_packaged
            self.description = analyses_packaged.__doc__
            try:
                self.analyses_author = analyses_packaged.__author__
            except AttributeError:
                logging.info('Analyses module does not have an author string.')
            try:
                self.analyses_version = analyses_packaged.__version__
            except AttributeError:
                logging.info('Analyses module does not have a version string.')

    def register_analyses(self):
        """Register analyses (analyses need to be imported first)."""

        for meta in Meta.all_instances:
            print 'Registering analysis meta information ' + meta.name + \
                  ' as blueprint in flask.'
            self.flask_app.register_blueprint(
                meta.blueprint,
                url_prefix='/'+meta.name
            )

            print 'Connect websockets to '+meta.name+'.'
            meta.wire_sockets(self.sockets, url_prefix='/'+meta.name)

    def render_index(self):
        """Render the List-of-Analyses overview page."""
        return render_template(
            'index.html',
            analyses=Meta.all_instances,
            analyses_author=self.analyses_author,
            analyses_version=self.analyses_version,
            description=self.description,
            databench_version=DATABENCH_VERSION
        )
