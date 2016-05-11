"""Main App."""

from __future__ import absolute_import, unicode_literals, division

from . import __version__ as DATABENCH_VERSION
from .analysis import Meta
from .analysis_zmq import MetaZMQ
from .readme import Readme
import glob
import logging
import os
import sys
import tornado.autoreload
import tornado.web
import zmq.eventloop

try:
    import glob2
except ImportError:
    glob2 = None

zmq.eventloop.ioloop.install()
log = logging.getLogger(__name__)


class App(object):
    """Databench app. Creates a Tornado app."""

    def __init__(self, zmq_port=None):

        self.info = {
            'title': 'Databench',
            'description': None,
            'author': None,
            'version': None,
        }
        self.metas = []

        self.routes = [
            (r'/(favicon\.ico)',
             tornado.web.StaticFileHandler,
             {'path': 'static/favicon.ico'}),

            (r'/_static/(.*)',
             tornado.web.StaticFileHandler,
             {'path': os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'static')}),

            (r'/_node_modules/(.*)',
             tornado.web.StaticFileHandler,
             {'path': os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'node_modules')}),

            (r'/',
             IndexHandler,
             {'info': self.info, 'metas': self.metas}),
        ]

        # check whether we have to determine zmq_port ourselves first
        if zmq_port is None:
            context = zmq.Context()
            socket = context.socket(zmq.PUB)
            zmq_port = socket.bind_to_random_port(
                'tcp://127.0.0.1',
                min_port=3000, max_port=9000,
            )
            socket.close()
            context.destroy()
            log.debug('determined: zmq_port={}'.format(zmq_port))

        self.spawned_analyses = {}

        self.zmq_pub_ctx = zmq.Context()
        self.zmq_pub = self.zmq_pub_ctx.socket(zmq.PUB)
        self.zmq_pub.bind('tcp://127.0.0.1:{}'.format(zmq_port))
        log.debug('main publishing to port {}'.format(zmq_port))

        self.zmq_pub_stream = zmq.eventloop.zmqstream.ZMQStream(
            self.zmq_pub,
            tornado.ioloop.IOLoop.current(),
        )

        self.analyses_info()

        self.metas += self.meta_analyses()
        self.metas += self.meta_analyses_py(self.zmq_pub_stream, zmq_port)
        self.metas += self.meta_analyses_pyspark(self.zmq_pub_stream, zmq_port)
        self.metas += self.meta_analyses_go(self.zmq_pub_stream, zmq_port)
        self.register_metas()

    def analyses_info(self):
        """Add analyses from the analyses folder."""

        if os.path.isfile('analyses/__init__.py'):
            sys.path.append('.')
            import analyses
            analyses_path = 'analyses'
        else:
            log.warning('Did not find "analyses" module. '
                        'Using packaged analyses.')
            from databench import analyses_packaged as analyses
            analyses_path = 'databench/analyses_packaged'

        self.info['author'] = getattr(analyses, '__author__', None)
        self.info['version'] = getattr(analyses, '__version__', None)
        self.info['logo_url'] = getattr(analyses, 'logo_url', None)
        self.info['title'] = getattr(analyses, 'title', None)

        readme = Readme(analyses_path)
        self.info['description'] = readme.text
        self.info.update(readme.meta)

        if self.info['logo_url'] is None:
            log.info('Analyses module does not specify a logo url.')
            self.info['logo_url'] = '/_static/logo.svg'
        if self.info['version'] is None:
            log.info('Analyses module does not specify a version.')
        if self.info['author'] is None:
            log.info('Analyses module does not specify an author.')
        if self.info['title'] is None:
            log.info('Analyses module does not specify a title.')
            self.info['title'] = 'Databench'

        # if 'analyses' contains a 'static' folder, make it available
        static_path = os.path.join(analyses_path, 'static')
        if os.path.isdir(static_path):
            log.debug('Making {} available under /static/.'
                      ''.format(static_path))

            self.routes.append((
                r'/static/(.*)',
                tornado.web.StaticFileHandler,
                {'path': static_path},
            ))
        else:
            log.debug('Did not find an analyses/static/ folder.')

        # if 'analyses' contains a 'node_modules' folder, make it available
        node_modules_path = os.path.join(analyses_path, 'node_modules')
        if os.path.isdir(node_modules_path):
            log.debug('Making {} available under /node_modules/.'
                      ''.format(node_modules_path))

            self.routes.append((
                r'/node_modules/(.*)',
                tornado.web.StaticFileHandler,
                {'path': node_modules_path},
            ))
        else:
            log.debug('Did not find an analyses/node_modules/ folder.')

    def meta_analyses(self):
        if os.path.isfile('analyses/__init__.py'):
            sys.path.append('.')
            import analyses
        else:
            log.debug('Did not find analyses. Using packaged analyses.')
            from . import analyses_packaged as analyses

        metas = []
        for name, analysis_class in analyses.analyses:
            log.debug('creating Meta for {}'.format(name))
            metas.append(Meta(name, analysis_class))
        return metas

    def meta_analyses_py(self, zmq_publish, zmq_port):
        analysis_folders = glob.glob('analyses/*_py')
        if not analysis_folders:
            analysis_folders = glob.glob('databench/analyses_packaged/*_py')

        metas = []
        for analysis_folder in analysis_folders:
            name = analysis_folder.rpartition('/')[2]
            if name[0] in ('.', '_'):
                continue
            log.debug('creating MetaZMQ for {}'.format(name))
            metas.append(MetaZMQ(
                name,
                ['python', '{}/analysis.py'.format(analysis_folder),
                 '--zmq-subscribe={}'.format(zmq_port)],
                zmq_publish,
            ))
        return metas

    def meta_analyses_pyspark(self, zmq_publish, zmq_port):
        analysis_folders = glob.glob('analyses/*_pyspark')
        if not analysis_folders:
            analysis_folders = glob.glob(
                'databench/analyses_packaged/*_pyspark'
            )

        metas = []
        for analysis_folder in analysis_folders:
            name = analysis_folder.rpartition('/')[2]
            if name[0] in ('.', '_'):
                continue
            log.debug('creating MetaZMQ for {}'.format(name))
            metas.append(MetaZMQ(
                name,
                ['pyspark', '{}/analysis.py'.format(analysis_folder),
                 '--zmq-subscribe={}'.format(zmq_port)],
                zmq_publish,
            ))
        return metas

    def meta_analyses_go(self, zmq_publish, zmq_port):
        analysis_folders = glob.glob('analyses/*_go')
        if not analysis_folders:
            analysis_folders = glob.glob('databench/analyses_packaged/*_go')

        metas = []
        for analysis_folder in analysis_folders:
            name = analysis_folder.rpartition('/')[2]
            if name[0] in ('.', '_'):
                continue
            log.info('installing {}'.format(name))
            os.system('cd {}; go install'.format(analysis_folder))
            log.debug('creating MetaZMQ for {}'.format(name))
            metas.append(MetaZMQ(
                name,
                [name, '--zmq-subscribe={}'.format(zmq_port)],
                zmq_publish,
            ))
        return metas

    def register_metas(self):
        """register metas"""
        watch_lists = []
        if 'watch' in self.info:
            watch_lists.append(self.info['watch'])

        for meta in self.metas:
            log.info('Registering meta information {}'.format(meta.name))
            self.routes += meta.routes

            if 'logo_url' in self.info and \
               'logo_url' not in meta.info:
                meta.info['logo_url'] = self.info['logo_url']

            if 'watch' in meta.info:
                watch_lists.append(meta.info['watch'])

        # process files to watch for autoreload
        if watch_lists:
            log.info('watching additional files: {}'.format(watch_lists))
            if glob2:
                files = glob2.glob(','.join(watch_lists))
            else:
                files = glob.glob(','.join(watch_lists))
                if any('**' in w for w in watch_lists):
                    log.warning('Please run "pip install glob2" to properly '
                                'process watch patterns with "**".')
            for fn in files:
                log.debug('watch file {}'.format(fn))
                tornado.autoreload.watch(fn)

    def build(self):
        """Run the build command specified in the Readme."""
        if 'build' not in self.info:
            return

        cmd = self.info['build']
        log.debug('building this command: {}'.format(cmd))
        os.system(cmd)

    def tornado_app(self, debug=False, template_path=None, **kwargs):
        if template_path is None:
            template_path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'templates',
            )

        if debug:
            self.build()

        return tornado.web.Application(
            self.routes,
            debug=debug,
            template_path=template_path,
            **kwargs
        )


class IndexHandler(tornado.web.RequestHandler):
    def initialize(self, info, metas):
        self.info = info
        self.metas = metas

    def get(self):
        """Render the List-of-Analyses overview page."""
        return self.render(
            'index.html',
            analyses=self.metas,
            databench_version=DATABENCH_VERSION,
            **self.info
        )
