"""Databench command line executable. Run to create a server that serves
the analyses pages and runs the python backend."""

import os
import sys
import glob
import codecs
import gevent
import logging
import argparse
import subprocess
import zmq.green as zmq

from flask.ext.socketio import SocketIO
from flask.ext.markdown import Markdown
from flask import copy_current_request_context
from flask import Flask, Blueprint, render_template

from .analysis import Analysis
from . import __version__ as DATABENCH_VERSION
from .analysis import LIST_ALL as LIST_ALL_ANALYSES


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
        self.heartbeat_timeout = 60*10000

        self.socketio = None
        self.description = None
        self.analyses_author = None
        self.analyses_version = None

        self.spawned_analyses = {}

        self.flask_app.debug = False
        self.flask_app.use_reloader = False
        self.flask_app.config['SECRET_KEY'] = 'ajksdfjhkasdfj'  # change

        if delimiters:
            self.custom_delimiters(delimiters)
        self.add_jinja2_highlight()
        self.add_read_file()
        self.add_markdown()
        self.register_analyses_pyspark()
        self.import_analyses()
        self.register_analyses()

        self.flask_app.add_url_rule('/', 'render_index', self.render_index)

    def run(self):
        """Entry point to run the app."""
        self.socketio.run(self.flask_app, host=self.host, port=self.port,
                          # transports=['websocket'],
                          policy_server=False,  # don't want to use Adobe Flash
                          heartbeat_timeout=self.heartbeat_timeout)

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

    def register_analyses_pyspark(self, port=8041):
        """Spawn processes for pyspark analyses."""

        self.zmq_socket_pub = zmq.Context().socket(zmq.PUB)
        self.zmq_socket_pub.bind('tcp://127.0.0.1:'+str(port))

        files = glob.glob('analyses_pyspark/*.py')
        pub_port = port+1
        for analysis_file in files:
            name = analysis_file[17:-3]

            # zmq subscription to listen for messages from backend
            logging.debug('main listening on port: '+str(pub_port))
            zmq_sub = zmq.Context().socket(zmq.SUB)
            zmq_sub.connect('tcp://127.0.0.1:'+str(pub_port))
            zmq_sub.setsockopt(zmq.SUBSCRIBE, '')

            analysis = Analysis(name, __name__, "Pyspark wrapper analysis.")
            analysis.blueprint = Blueprint(
                name,
                __name__,
                template_folder=os.getcwd()+'/analyses_pyspark/templates',
                static_folder=os.getcwd()+'/analyses_pyspark/static',
            )
            analysis.blueprint.add_url_rule('/', 'render_index',
                                            analysis.render_index)
            if name in self.spawned_analyses:
                del self.spawned_analyses[name][0]
                self.spawned_analyses[name][1].terminate()
                self.spawned_analyses[name][3].close()
                if self.spawned_analyses[name][4]:
                    self.spawned_analyses[name][4].join()
            self.spawned_analyses[name] = [
                analysis,
                subprocess.Popen(['pyspark', analysis_file], shell=False),
                pub_port,
                zmq_sub,
                None
            ]
            analysis.signals.zmq_sub = zmq_sub
            analysis.signals.pub_port = pub_port
            analysis.signals.listeners = []

            @analysis.signals.on('connect')
            def onconnect():

                # clean up possible old listeners
                if self.spawned_analyses[analysis.name][4]:
                    self.spawned_analyses[analysis.name][4].kill()

                def process_message(json):
                    if 'action' in json and json['action'] == 'emit':
                        logging.debug('emitting to frontend: '+str(json))
                        analysis.signals.emit(json['signal'], json['message'])
                    elif 'action' in json and \
                         json['action'] == 'listeners_list':
                        analysis.signals.listeners_list = json['listeners']
                        for listener in analysis.signals.listeners_list:
                            logging.debug('----------'+listener)
                            if listener == 'connect':
                                logging.debug('Adding connect here would leed '
                                              'to conflicts. Skipping.')
                                continue
                            if listener not in analysis.signals.listeners:
                                analysis.signals.on(listener)(
                                    lambda *args: self.zmq_socket_pub.send_json({
                                        '__databench_namespace': analysis.name,
                                        'action': 'event',
                                        'event': listener,
                                        'event_message': args,
                                    })
                                )
                                analysis.signals.listeners.append(listener)

                @copy_current_request_context
                def zmq_listener():
                    while True:
                        msg = analysis.signals.zmq_sub.recv_json()
                        logging.debug('main ('+analysis.name+') received '
                                      'msg: '+str(msg))
                        if '__databench_namespace' in msg:
                            if analysis.name != msg['__databench_namespace']:
                                logging.warn('__databench_namespace is not '
                                             'equal to analysis name')
                            del msg['__databench_namespace']
                            process_message(msg)
                self.spawned_analyses[analysis.name][4] = \
                    gevent.Greenlet.spawn(zmq_listener)

                logging.debug('init kernel '+analysis.name+' to publish on '
                              'port '+str(analysis.signals.pub_port))
                self.zmq_socket_pub.send_json({
                    '__databench_namespace': analysis.name,
                    'publish_on_port': analysis.signals.pub_port,
                })

                logging.debug('trigger on_connect on kernel')
                self.zmq_socket_pub.send_json({
                    '__databench_namespace': analysis.name,
                    'action': 'event',
                    'event': 'connect',
                    'event_message': [],
                })

            pub_port += 1

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
        except ImportError:
            # Check whether there are already some analyses registered and if
            # so, don't register the prepackaged analyses.
            if LIST_ALL_ANALYSES:
                return

            print "Did not find 'analyses' module."
            logging.debug('sys.path: '+str(sys.path))
            logging.debug('os.path.dirname(os.path.realpath(__file__): ' +
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
    parser.add_argument('--heartbeat_timeout', dest='heartbeat_timeout',
                        type=int, default=60*10000,
                        help='set heartbeat_timeout for SocketIO')
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
    app.heartbeat_timeout = args.heartbeat_timeout
    app.run()

    return app


if __name__ == '__main__':
    run()
