"""Databench command line executable. Run to create a server that serves
the analyses pages and runs the python backend."""

import os
import sys
import glob
import codecs
import logging
import argparse
import zmq.green as zmq

import flask_sockets
from flask.ext.markdown import Markdown
from flask import Flask, render_template

from .analysis import MetaZMQ
from . import __version__ as DATABENCH_VERSION
from .analysis import LIST_ALL_META


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
        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler
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

    def register_analyses_py(self, zmq_publish, sub_port=8042):
        analysis_folders = glob.glob('analyses/*_py')
        if not analysis_folders:
            analysis_folders = glob.glob('analyses_packaged/*_py')

        for analysis_folder in analysis_folders:
            name = analysis_folder[analysis_folder.find('/')+1:]
            logging.debug('creating MetaZMQ for '+name)
            MetaZMQ(name, __name__, "ZMQ Analysis py",
                    ['python', analysis_folder+'/analysis.py'],
                    zmq_publish, sub_port)
            sub_port += 1

    def register_analyses_pyspark(self, zmq_publish, sub_port=8142):
        analysis_folders = glob.glob('analyses/*_pyspark')
        if not analysis_folders:
            analysis_folders = glob.glob('analyses_packaged/*_pyspark')

        for analysis_folder in analysis_folders:
            name = analysis_folder[analysis_folder.find('/')+1:]
            logging.debug('creating MetaZMQ for '+name)
            MetaZMQ(name, __name__, "ZMQ Analysis py",
                    ['pyspark', analysis_folder+'/analysis.py'],
                    zmq_publish, sub_port)
            sub_port += 1

    def register_analyses_go(self, zmq_publish, sub_port=8042):
        analysis_folders = glob.glob('analyses/*_go')
        if not analysis_folders:
            analysis_folders = glob.glob('analyses_packaged/*_go')

        for analysis_folder in analysis_folders:
            name = analysis_folder[analysis_folder.find('/')+1:]
            logging.info('installing '+name)
            os.system('cd '+analysis_folder+'; go install')
            logging.debug('creating MetaZMQ for '+name)
            MetaZMQ(name, __name__, "ZMQ Analysis go",
                    [name],
                    zmq_publish, sub_port)
            sub_port += 1

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

        for meta in LIST_ALL_META:
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
            analyses=LIST_ALL_META,
            analyses_author=self.analyses_author,
            analyses_version=self.analyses_version,
            description=self.description,
            databench_version=DATABENCH_VERSION
        )


def run():
    """Entry point to run databench."""

    parser = argparse.ArgumentParser(description=__doc__,
                                     version=DATABENCH_VERSION)
    parser.add_argument('--log', dest='loglevel', default="NOTSET",
                        help='set log level')
    parser.add_argument('--host', dest='host',
                        default=os.environ.get('HOST', 'localhost'),
                        help='set host for webserver')
    parser.add_argument('--port', dest='port',
                        type=int, default=int(os.environ.get('PORT', 5000)),
                        help='set port for webserver')
    delimiter_args = parser.add_argument_group('delimiters')
    delimiter_args.add_argument('--variable_start_string',
                                help='delimiter for variable start')
    delimiter_args.add_argument('--variable_end_string',
                                help='delimiter for variable end')
    delimiter_args.add_argument('--block_start_string',
                                help='delimiter for block start')
    delimiter_args.add_argument('--block_end_string',
                                help='delimiter for block end')
    delimiter_args.add_argument('--comment_start_string',
                                help='delimiter for comment start')
    delimiter_args.add_argument('--comment_end_string',
                                help='delimiter for comment end')
    args = parser.parse_args()

    # log
    if args.loglevel != 'NOTSET':
        print 'Setting loglevel to '+args.loglevel+'.'
        logging.basicConfig(level=getattr(logging, args.loglevel))

    # delimiters
    delimiters = {
        'variable_start_string': '[[',
        'variable_end_string': ']]',
    }
    if args.variable_start_string:
        delimiters['variable_start_string'] = args.variable_start_string
    if args.variable_end_string:
        delimiters['variable_end_string'] = args.variable_end_string
    if args.block_start_string:
        delimiters['block_start_string'] = args.block_start_string
    if args.block_end_string:
        delimiters['block_end_string'] = args.block_end_string
    if args.comment_start_string:
        delimiters['comment_start_string'] = args.comment_start_string
    if args.comment_end_string:
        delimiters['comment_end_string'] = args.comment_end_string

    print '--- databench v'+DATABENCH_VERSION+' ---'
    logging.info('host='+str(args.host)+', port='+str(args.port))
    logging.info('delimiters='+str(delimiters))
    app = App(__name__, host=args.host, port=args.port, delimiters=delimiters)
    app.run()

    return app


if __name__ == '__main__':
    run()
