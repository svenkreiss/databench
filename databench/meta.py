"""Analysis module for Databench."""

from __future__ import absolute_import, unicode_literals, division

import json
import logging
import tornado.gen
import tornado.web
import tornado.websocket

try:
    from urllib.parse import parse_qs  # Python 3
except ImportError:
    from urlparse import parse_qs  # Python 2

from . import __version__ as DATABENCH_VERSION
from .utils import json_encoder_default

PING_INTERVAL = 15000
log = logging.getLogger(__name__)


class Meta(object):
    """Meta class referencing an analysis.

    :param str name: Name of this analysis.
    :param databench.Analysis analysis_class:
        Object that should be instantiated for every new websocket connection.
    :param str analysis_path: Path of the analysis class.
    :param list extra_routes: [(route, handler, data), ...]
    :param list cli_args: Arguments from the command line.
    """

    def __init__(self, name, analysis_class, analysis_path, extra_routes,
                 cli_args=None):
        self.name = name
        self.analysis_class = analysis_class
        self.analysis_path = analysis_path
        self.cli_args = cli_args

        self.info = {}
        self.routes = [
            (r'/{}/static/(.*)'.format(self.name),
             tornado.web.StaticFileHandler,
             {'path': self.analysis_path}),

            (r'/{}/ws'.format(self.name),
             FrontendHandler,
             {'meta': self}),

            (r'/(?P<template_name>{}/.+\.html)'.format(self.name),
             RenderTemplate,
             {'info': self.info}),

            (r'/{}/'.format(self.name),
             RenderTemplate,
             {'template_name': '{}/index.html'.format(self.name),
              'info': self.info}),
        ] + [
            (r'/{}/{}'.format(self.name, route), handler, data)
            for route, handler, data in extra_routes
        ]

    @staticmethod
    @tornado.gen.coroutine
    def run_process(analysis, action_name, message='__nomessagetoken__'):
        """Executes an action in the analysis with the given message.

        It also handles the start and stop signals in the case that message
        is a `dict` with a key ``__process_id``.

        :param str action_name: Name of the action to trigger.
        :param message: Message.
        :param callback:
            A callback function when done (e.g.
            `~tornado.testing.AsyncTestCase.stop` in tests).
        :rtype: tornado.concurrent.Future
        """

        if analysis is None:
            return

        # detect process_id
        process_id = None
        if isinstance(message, dict) and '__process_id' in message:
            process_id = message['__process_id']
            del message['__process_id']

        if process_id:
            analysis.emit('__process', {'id': process_id, 'status': 'start'})

        fn_name = 'on_{}'.format(action_name)
        fn = getattr(analysis, fn_name, None)
        if fn is not None:
            log.debug('calling {}'.format(fn_name))

            # Check whether this is a list (positional arguments)
            # or a dictionary (keyword arguments).
            if isinstance(message, list):
                yield tornado.gen.maybe_future(fn(*message))
            elif isinstance(message, dict):
                yield tornado.gen.maybe_future(fn(**message))
            elif message == '__nomessagetoken__':
                yield tornado.gen.maybe_future(fn())
            else:
                yield tornado.gen.maybe_future(fn(message))
        else:
            # default is to store action name and data as key and value
            # in analysis.data
            analysis.data[action_name] = (
                message if message != '__nomessagetoken__' else None)

        if process_id:
            analysis.emit('__process', {'id': process_id, 'status': 'end'})


class FrontendHandler(tornado.websocket.WebSocketHandler):

    def initialize(self, meta):
        self.meta = meta
        self.analysis = None
        self.ping_callback = tornado.ioloop.PeriodicCallback(self.do_ping,
                                                             PING_INTERVAL)
        self.ping_callback.start()
        tornado.autoreload.add_reload_hook(self.on_close)

    def do_ping(self):
        if self.ws_connection is None:
            self.ping_callback.stop()
            return
        self.ping(b'')

    def open(self):
        log.debug('WebSocket connection opened.')

    @tornado.gen.coroutine
    def on_close(self):
        log.debug('WebSocket connection closed.')
        yield self.meta.run_process(self.analysis, 'disconnected')

    @tornado.gen.coroutine
    def on_message(self, message):
        if message is None:
            log.debug('empty message received.')
            return

        msg = json.loads(message)
        if '__connect' in msg:
            if self.analysis is not None:
                log.error('Connection already has an analysis. Abort.')
                return

            requested_id = msg['__connect']
            log.debug('Instantiate analysis with id {}'.format(requested_id))
            self.analysis = self.meta.analysis_class()
            self.analysis.init_databench(requested_id)
            self.analysis.set_emit_fn(self.emit)
            log.info('Analysis {} instanciated.'.format(self.analysis.id_))
            yield self.emit('__connect', {'analysis_id': self.analysis.id_})

            yield self.meta.run_process(self.analysis, 'connect')

            args = {'cli_args': None, 'request_args': None}
            if self.meta.cli_args is not None:
                args['cli_args'] = self.meta.cli_args
            if '__request_args' in msg and msg['__request_args']:
                args['request_args'] = parse_qs(
                    msg['__request_args'].lstrip('?'))
            yield self.meta.run_process(self.analysis, 'args', args)

            yield self.meta.run_process(self.analysis, 'connected')
            log.info('Connected to analysis.')
            return

        if self.analysis is None:
            log.warning('no analysis connected. Abort.')
            return

        if 'signal' not in msg:
            log.info('message not processed: {}'.format(message))
            return

        if 'load' not in msg:
            yield self.meta.run_process(self.analysis,
                                        msg['signal'])
        else:
            yield self.meta.run_process(self.analysis,
                                        msg['signal'], msg['load'])

    def emit(self, signal, message='__nomessagetoken__'):
        data = {'signal': signal}
        if message != '__nomessagetoken__':
            data['load'] = message

        try:
            return self.write_message(
                json.dumps(data, default=json_encoder_default).encode('utf-8'))
        except tornado.websocket.WebSocketClosedError:
            pass


class RenderTemplate(tornado.web.RequestHandler):
    def initialize(self, info, template_name=None):
        self.info = info
        self.template_name = template_name

    def get(self, template_name=None):
        if template_name is None:
            template_name = self.template_name
        self.render(template_name,
                    databench_version=DATABENCH_VERSION,
                    **self.info)
