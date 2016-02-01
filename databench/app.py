"""Main Flask App."""

import os
import sys
import glob
import time
import logging
import traceback
import zmq.eventloop

import tornado.web

from .analysis import Meta
from .analysis_zmq import MetaZMQ
from . import __version__ as DATABENCH_VERSION

log = logging.getLogger(__name__)


class App(object):
    """Databench app. The Tornado app is either injected or created.

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

    def __init__(self, zmq_port=None, template_delimiters=None):

        self.info = {
            'logo_url': '/static/logo.svg',
            'title': 'Databench',
            'description': None,
            'author': None,
            'version': None,
        }

        self.routes = [
            (r'/favicon\.ico',
             tornado.web.StaticFileHandler,
             {'path': 'static/favicon.ico'}),
            (r'/static/(.*)',
             tornado.web.StaticFileHandler,
             {'path': os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'static')}),
            (r'/',
             IndexHandler,
             {'info': self.info}),
        ]

        # check whether we have to determine zmq_port ourselves first
        if zmq_port is None:
            context = zmq.Context()
            socket = context.socket(zmq.PUB)
            zmq_port = socket.bind_to_random_port(
                'tcp://127.0.0.1',
                min_port=3000, max_port=9000,
            )
            context.destroy()
            log.debug('determined: zmq_port={}'.format(zmq_port))

        self.spawned_analyses = {}

        # if template_delimiters is not None:
        #     self.custom_delimiters(template_delimiters)

        zmq_publish = zmq.Context().socket(zmq.PUB)
        zmq_publish.bind('tcp://127.0.0.1:{}'.format(zmq_port))
        log.debug('main publishing to port {}'.format(zmq_port))

        time.sleep(2.5)

        self.register_analyses_py(zmq_publish, zmq_port)
        # self.register_analyses_pyspark(zmq_publish)
        # self.register_analyses_go(zmq_publish)
        self.import_analyses()
        self.register_analyses()

    def tornado_app(self):
        return tornado.web.Application(self.routes)

    # def custom_delimiters(self, delimiters):
    #     """Change the standard jinja2 delimiters to allow those delimiters be
    #     used by frontend template engines."""
    #     options = self.flask_app.jinja_options.copy()
    #     options.update(delimiters)
    #     self.flask_app.jinja_options = options

    def register_analyses_py(self, zmq_publish, zmq_port):
        analysis_folders = glob.glob('analyses/*_py')
        if not analysis_folders:
            analysis_folders = glob.glob('databench/analyses_packaged/*_py')

        for analysis_folder in analysis_folders:
            name = analysis_folder[analysis_folder.rfind('/')+1:]
            if name[0] in ['.', '_']:
                continue
            log.debug('creating MetaZMQ for {}'.format(name))
            MetaZMQ(name, __name__, "ZMQ Analysis py",
                    ['python', analysis_folder+'/analysis.py',
                     '--zmq-port={}'.format(zmq_port)],
                    zmq_publish)

    def register_analyses_pyspark(self, zmq_publish):
        analysis_folders = glob.glob('analyses/*_pyspark')
        if not analysis_folders:
            analysis_folders = glob.glob(
                'databench/analyses_packaged/*_pyspark'
            )

        for analysis_folder in analysis_folders:
            name = analysis_folder[analysis_folder.rfind('/')+1:]
            if name[0] in ['.', '_']:
                continue
            log.debug('creating MetaZMQ for '+name)
            MetaZMQ(name, __name__, "ZMQ Analysis py",
                    ['pyspark', analysis_folder+'/analysis.py'],
                    zmq_publish)

    def register_analyses_go(self, zmq_publish):
        analysis_folders = glob.glob('analyses/*_go')
        if not analysis_folders:
            analysis_folders = glob.glob('databench/analyses_packaged/*_go')

        for analysis_folder in analysis_folders:
            name = analysis_folder[analysis_folder.rfind('/')+1:]
            if name[0] in ['.', '_']:
                continue
            log.info('installing '+name)
            os.system('cd '+analysis_folder+'; go install')
            log.debug('creating MetaZMQ for '+name)
            MetaZMQ(name, __name__, "ZMQ Analysis go",
                    [name], zmq_publish)

    def import_analyses(self):
        """Add analyses from the analyses folder."""

        sys.path.append('.')
        try:
            import analyses
        except ImportError as e:
            if str(e).replace("'", "") != 'No module named analyses':
                traceback.print_exc(file=sys.stdout)
                raise e

            print('Did not find "analyses" module. Using packaged analyses.')
            from databench import analyses_packaged as analyses

        self.info['description'] = analyses.__doc__
        try:
            self.info['author'] = analyses.__author__
        except AttributeError:
            log.info('Analyses module does not have an author string.')
        try:
            self.info['version'] = analyses.__version__
        except AttributeError:
            log.info('Analyses module does not have a version string.')
        try:
            self.info['logo_url'] = analyses.logo_url
        except AttributeError:
            log.info('Analyses module does not specify a logo url.')
        try:
            self.info['title'] = analyses.title
        except AttributeError:
            log.info('Analyses module does not specify a title.')

        # if main analyses folder contains a 'static' folder, make it available
        static_path = os.path.join(os.getcwd(), 'analyses', 'static')
        if not os.path.isdir(static_path):
            static_path = os.path.join(
                os.getcwd(), 'databench', 'analyses_packaged', 'static',
            )
        if os.path.isdir(static_path):
            log.debug('Making {} available under analyses_static/.'
                          ''.format(static_path))

            self.routes.append((
                r'/analyses_static/(.*)',
                tornado.web.StaticFileHandler,
                {'path': static_path},
            ))
        else:
            log.debug('Did not find an analyses/static/ folder. ' +
                          'Checked: {}'.format(static_path))

    def register_analyses(self):
        """Register analyses (analyses need to be imported first)."""

        for meta in Meta.all_instances:
            print('Registering meta information {}'.format(meta.name))
            self.routes += meta.routes

            meta.info = self.info

            # log.debug('Connect websockets to '+meta.name+'.')
            # meta.wire_sockets(self.sockets, url_prefix='/'+meta.name)


class IndexHandler(tornado.web.RequestHandler):
    def initialize(self, info):
        self.info = info

    def get(self):
        """Render the List-of-Analyses overview page."""
        return self.render(
            'templates/index.html',
            analyses=Meta.all_instances,
            info=self.info,
            databench_version=DATABENCH_VERSION,
        )
