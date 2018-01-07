"""Main App."""

from __future__ import absolute_import, unicode_literals, division

from . import __version__ as DATABENCH_VERSION
from .meta import Meta
from .meta_zmq import MetaZMQ
from .readme import Readme
from .template import Loader
import glob
import importlib
import logging
import os
import random
import subprocess
import sys
import tornado.autoreload
import tornado.web
import yaml
import zmq.eventloop

try:
    import glob2
except ImportError:
    glob2 = None

zmq.eventloop.ioloop.install()
log = logging.getLogger(__name__)


class App(object):
    """Databench app. Creates a Tornado app.

    :param str analyses_path: An import path of the analyses.
    :param int zmq_port: Force to use the given ZMQ port for publishing.
    """

    def __init__(self, analyses_path=None, zmq_port=None, cli_args=None,
                 debug=False):
        self.cli_args = cli_args
        self.debug = debug
        self.info = {
            'title': 'Databench',
            'description': None,
            'description_html': None,
            'author': None,
            'version': '0.0.0',
        }
        self.metas = []
        self.spawned_analyses = {}
        self.analyses, self.analyses_path = self.get_analyses(analyses_path)

        self.routes = [
            (r'/(?:index.html)?', IndexHandler,
             {'info': self.info, 'metas': self.metas}),
        ] + self.static_routes()

        self.init_zmq(zmq_port)
        self.analyses_info()
        self.meta_analyses()
        self.register_metas()

    def init_zmq(self, zmq_port=None):
        # check whether we have to determine zmq_port ourselves first
        if zmq_port is None:
            context = zmq.Context()
            socket = context.socket(zmq.PUB)
            zmq_port = socket.bind_to_random_port(
                'tcp://127.0.0.1', min_port=6000,
            )
            socket.close()
            context.destroy()
            log.debug('determined: zmq_port={}'.format(zmq_port))
        self.zmq_port = zmq_port

        self.zmq_pub_ctx = zmq.Context()
        self.zmq_pub = self.zmq_pub_ctx.socket(zmq.PUB)
        self.zmq_pub.bind('tcp://127.0.0.1:{}'.format(zmq_port))
        log.debug('main publishing to port {}'.format(zmq_port))

        self.zmq_pub_stream = zmq.eventloop.zmqstream.ZMQStream(
            self.zmq_pub,
            tornado.ioloop.IOLoop.current(),
        )

    @staticmethod
    def static_routes():
        static_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'static')
        node_modules_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'node_modules')

        # watch Databench's own static files
        tornado.autoreload.watch(os.path.join(static_path, 'databench.js'))
        tornado.autoreload.watch(os.path.join(static_path, 'databench.css'))

        return [
            (r'/(favicon\.ico)', tornado.web.StaticFileHandler,
             {'path': 'static/favicon.ico'}),

            (r'/_static/(.*)', tornado.web.StaticFileHandler,
             {'path': static_path}),

            (r'/_node_modules/(.*)', tornado.web.StaticFileHandler,
             {'path': node_modules_path}),
        ]

    @staticmethod
    def get_analyses(analyses_path):
        if analyses_path:
            # analyses path supplied manually
            orig_syspath = sys.path
            sys.path.insert(0, '.')
            analyses = importlib.import_module(analyses_path)
            sys.path = orig_syspath
        elif os.path.isfile(os.path.join('analyses', 'index.yaml')):
            # cwd outside analyses
            orig_syspath = sys.path
            sys.path.insert(0, '.')
            import analyses
            sys.path = orig_syspath
        elif os.path.isfile('index.yaml'):
            # cwd is inside analyses
            orig_syspath = sys.path
            sys.path.insert(0, '..')
            import analyses
            sys.path = orig_syspath
        else:
            log.warning('Did not find "analyses" module. '
                        'Using packaged analyses.')
            from databench import analyses_packaged as analyses

        analyses_path = os.path.abspath(os.path.dirname(analyses.__file__))
        return analyses, analyses_path

    def analyses_info(self):
        """Add analyses from the analyses folder."""
        f_config = os.path.join(self.analyses_path, 'index.yaml')
        tornado.autoreload.watch(f_config)
        with open(f_config, 'r') as f:
            config = yaml.safe_load(f)
            self.info.update(config)
        if self.debug:
            self.info['version'] += '.debug-{:04X}'.format(
                int(random.random() * 0xffff))

        readme = Readme(self.analyses_path)
        if self.info['description'] is None:
            self.info['description'] = readme.text.strip()
        self.info['description_html'] = readme.html

        # If 'analyses', 'analyses/..' or current directory contains a
        # 'static' folder, make it available.
        static_path = next((
            p
            for p in (os.path.join(self.analyses_path, 'static'),
                      os.path.join(self.analyses_path, '..', 'static'),
                      os.path.join(os.getcwd(), 'static'))
            if os.path.isdir(p)
        ), None)
        if static_path is not None:
            log.debug('Making {} available at /static/.'.format(static_path))
            self.routes.append(
                (r'/static/(.*)', tornado.web.StaticFileHandler,
                 {'path': static_path})
            )
        else:
            log.debug('Did not find a static folder.')

        # If 'analyses', 'analyses/..' or current directory contains a
        # 'node_modules' folder, make it available.
        node_modules_path = next((
            p
            for p in (os.path.join(self.analyses_path, 'node_modules'),
                      os.path.join(self.analyses_path, '..', 'node_modules'),
                      os.path.join(os.getcwd(), 'node_modules'))
            if os.path.isdir(p)
        ), None)
        if node_modules_path is not None:
            log.debug('Making {} available at /node_modules/.'
                      ''.format(node_modules_path))
            self.routes.append(
                (r'/node_modules/(.*)', tornado.web.StaticFileHandler,
                 {'path': node_modules_path})
            )
        else:
            log.debug('Did not find a node_modules folder.')

    def meta_analyses(self):
        for analysis_info in self.info['analyses']:
            name = analysis_info.get('name', None)
            if name is None:
                continue
            path = os.path.join(self.analyses_path, name)
            if not os.path.isdir(path):
                log.warning('directory {} not found'.format(path))
                continue

            meta = None
            analysis_kernel = analysis_info.get('kernel', None)
            if analysis_kernel is None:
                meta = self.meta_analysis_nokernel(name, path)
            elif analysis_kernel == 'py':
                meta = self.meta_analysis_py(name, path)
            elif analysis_kernel == 'pyspark':
                meta = self.meta_analysis_pyspark(name, path)
            elif analysis_kernel == 'go':
                meta = self.meta_analysis_go(name, path)

            if meta is None:
                continue
            meta.fill_info(version=self.info['version'],
                           home_link='/',
                           **analysis_info)
            self.metas.append(meta)

    def meta_analysis_nokernel(self, name, path):
        try:
            analysis_file = importlib.import_module('.' + name + '.analysis',
                                                    self.analyses.__name__)
        except ImportError:
            log.warning('could not import analysis {}'.format(name),
                        exc_info=True)
            return
        items = [getattr(analysis_file, item)
                 for item in dir(analysis_file)
                 if not item.startswith('__')]
        classes = [ac for ac in items
                   if hasattr(ac, '_databench_analysis')]
        if not classes:
            log.warning('no Analysis class found for {}'.format(name))
            return
        log.debug('creating Meta for {}'.format(name))
        return Meta(
            name,
            classes[0],
            path,
            self.extra_routes(name, path),
            self.cli_args,
        )

    def meta_analysis_py(self, name, path):
        log.debug('creating MetaZMQ for {}'.format(name))
        return MetaZMQ(
            name,
            ['python', os.path.join(path, 'analysis.py'),
             '--zmq-subscribe={}'.format(self.zmq_port)],
            self.zmq_pub_stream,
            path,
            self.extra_routes(name, path),
        )

    def meta_analysis_pyspark(self, name, path):
        log.debug('creating MetaZMQ for {}'.format(name))
        return MetaZMQ(
            name,
            ['pyspark', '{}/analysis.py'.format(path),
             '--zmq-subscribe={}'.format(self.zmq_port)],
            self.zmq_pub_stream,
            path,
            self.extra_routes(name, path),
        )

    def meta_analysis_go(self, name, path):
        log.info('installing {}'.format(name))
        os.system('cd {}; go install'.format(path))
        log.debug('creating MetaZMQ for {}'.format(name))
        return MetaZMQ(
            name,
            [name, '--zmq-subscribe={}'.format(self.zmq_port)],
            self.zmq_pub_stream,
            path,
            self.extra_routes(name, path),
        )

    def extra_routes(self, name, path):
        if not os.path.isfile(os.path.join(path, 'routes.py')):
            return []

        routes_file = importlib.import_module('.' + name + '.routes',
                                              self.analyses.__name__)

        if not hasattr(routes_file, 'ROUTES'):
            log.warning('no extra routes found for {}'.format(name))
            return []
        return routes_file.ROUTES

    def register_metas(self):
        """register metas"""

        # concatenate some attributes to global lists:
        aggregated = {'build': [], 'watch': []}
        for attribute, values in aggregated.items():
            for info in self.info['analyses'] + [self.info]:
                if attribute in info:
                    values.append(info[attribute])

        for meta in self.metas:
            log.debug('Registering meta information {}'.format(meta.name))

            # grab routes
            self.routes += [(r'/{}/{}'.format(meta.name, route),
                             handler, data)
                            for route, handler, data in meta.routes]

        # process files to watch for autoreload
        if aggregated['watch']:
            to_watch = [expr for w in aggregated['watch'] for expr in w]
            log.info('watching additional files: {}'.format(to_watch))

            cwd = os.getcwd()
            os.chdir(self.analyses_path)
            if glob2:
                files = [os.path.join(self.analyses_path, fn)
                         for expr in to_watch for fn in glob2.glob(expr)]
            else:
                files = [os.path.join(self.analyses_path, fn)
                         for expr in to_watch for fn in glob.glob(expr)]
                if any('**' in expr for expr in to_watch):
                    log.warning('Please run "pip install glob2" to properly '
                                'process watch patterns with "**".')
            os.chdir(cwd)

            for fn in files:
                log.debug('watch file {}'.format(fn))
                tornado.autoreload.watch(fn)

        # save build commands
        self.build_cmds = aggregated['build']

    def build(self):
        """Run the build command specified in index.yaml."""
        for cmd in self.build_cmds:
            log.info('building command: {}'.format(cmd))
            full_cmd = 'cd {}; {}'.format(self.analyses_path, cmd)
            log.debug('full command: {}'.format(full_cmd))
            subprocess.call(full_cmd, shell=True)
            log.info('build done')

    def tornado_app(self, template_path=None, **kwargs):
        if template_path is None:
            template_path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'templates',
            )

        if self.debug:
            self.build()

        return tornado.web.Application(
            self.routes,
            debug=self.debug,
            template_loader=Loader([self.analyses_path, template_path]),
            **kwargs
        )


class IndexHandler(tornado.web.RequestHandler):
    def initialize(self, info, metas):
        self.info = info
        self.metas = metas

    def meta_infos(self):
        return [{
            'name': meta.name,
            'title': meta.info['title'],
            'description': meta.info['description'],
            'show_in_index': meta.info['show_in_index'],
            'thumbnail': meta.info['thumbnail'],
        } for meta in self.metas]

    def get(self):
        """Render the List-of-Analyses overview page."""
        return self.render(
            'index.html',
            databench_version=DATABENCH_VERSION,
            meta_infos=self.meta_infos(),
            **self.info
        )


class SingleApp(object):
    def __init__(self, analysis, name=None, title=None, path=None,
                 cli_args=None, debug=False, version='0.0.0', **kwargs):
        if name is None and title is None:
            name = analysis.__name__.lower()
            title = analysis.__name__
        if title is None:
            title = name
        if name is None:
            name = analysis.__name__.lower()
        if path is None:
            path = __file__

        self.debug = debug
        self.routes = App.static_routes()

        self.meta = Meta(
            name,
            analysis,
            os.path.abspath(os.path.dirname(path)),
            kwargs.get('extra_routes', []),
            cli_args,
            **kwargs
        )
        self.meta.fill_info(name=name, title=title, version=version)
        self.routes += [(r'/{}'.format(route), handler, data)
                        for route, handler, data in self.meta.routes]

    def tornado_app(self, template_path=None, **kwargs):
        if template_path is None:
            template_path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'templates',
            )

        return tornado.web.Application(
            self.routes,
            debug=self.debug,
            template_loader=Loader([template_path]),
            **kwargs
        )
