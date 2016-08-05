"""Analysis module for Databench."""

from __future__ import absolute_import, unicode_literals, division

import json
import logging
import os
import tornado.gen
import tornado.web
import tornado.websocket

try:
    from urllib.parse import parse_qs  # Python 3
except ImportError:
    from urlparse import parse_qs  # Python 2

from . import __version__ as DATABENCH_VERSION
from .utils import sanitize_message

PING_INTERVAL = 15000
log = logging.getLogger(__name__)


class Meta(object):
    """Meta class referencing an analysis.

    :param str name:
        Name of this analysis. If ``signals`` is not specified,
        this also becomes the namespace for the WebSocket connection and
        has to match the frontend's :js:class:`Databench` ``name``.

    :param analysis_class:
        Object that should be instantiated for every new websocket connection.
    :type analysis_class: :class:`databench.Analysis`

    :param str analysis_path: Path of the analysis class.

    :param list extra_routes: [(route, handler, data), ...]
    """

    def __init__(self, name, analysis_class, analysis_path, extra_routes):
        self.name = name
        self.analysis_class = analysis_class
        self.analysis_path = analysis_path

        self.info = {}
        self.routes = [
            (r'/{}/static/(.*)'.format(self.name),
             tornado.web.StaticFileHandler,
             {'path': self.analysis_path}),

            (r'/{}/ws'.format(self.name),
             FrontendHandler,
             {'meta': self}),

            (r'/{}/(?P<template_name>.+\.html)'.format(self.name),
             RenderTemplate,
             {'template_path': self.analysis_path,
              'info': self.info}),

            (r'/{}/'.format(self.name),
             RenderTemplate,
             {'template_name': 'index.html',
              'template_path': self.analysis_path,
              'info': self.info}),
        ] + [
            (r'/{}/{}'.format(self.name, route), handler, data)
            for route, handler, data in extra_routes
        ]

    @tornado.gen.coroutine
    def run_process(self, analysis, action_name, message='__nomessagetoken__'):
        """Executes an action in the analysis with the given message.

        It also handles the start and stop signals in case a ``__process_id``
        is given.
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
        if hasattr(analysis, fn_name):
            log.debug('calling {}'.format(fn_name))
            fn = getattr(analysis, fn_name)

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
                message
                if message != '__nomessagetoken__'
                else None
            )

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

    def on_close(self):
        log.debug('WebSocket connection closed.')
        self.meta.run_process(self.analysis, 'disconnected')

    def on_message(self, message):
        if message is None:
            log.debug('empty message received.')
            return

        msg = json.loads(message)
        if '__connect' in msg:
            if self.analysis is not None:
                log.error('Connection already has an analysis. Abort.')
                return

            log.debug('Instantiate analysis id {}'.format(msg['__connect']))
            self.analysis = self.meta.analysis_class(msg['__connect'])
            self.analysis.set_emit_fn(self.emit)
            log.info('Analysis {} instanciated.'.format(self.analysis.id_))
            self.emit('__connect', {'analysis_id': self.analysis.id_})

            self.meta.run_process(self.analysis, 'connect')
            log.info('Connected to analysis.')

            if '__request_args' in msg and msg['__request_args']:
                qs = parse_qs(msg['__request_args'].lstrip('?'))
                self.meta.run_process(self.analysis, 'request_args', [qs])
            return

        if self.analysis is None:
            log.warning('no analysis connected. Abort.')
            return

        if 'signal' not in msg:
            log.info('message not processed: {}'.format(message))
            return

        if 'load' not in msg:
            self.meta.run_process(self.analysis, msg['signal'])
        else:
            self.meta.run_process(self.analysis, msg['signal'], msg['load'])

    @tornado.gen.coroutine
    def emit(self, signal, message='__nomessagetoken__'):
        message = sanitize_message(message)

        data = {'signal': signal}
        if message != '__nomessagetoken__':
            data['load'] = message

        try:
            self.write_message(json.dumps(data).encode('utf-8'))
        except tornado.websocket.WebSocketClosedError:
            pass


class RenderTemplate(tornado.web.RequestHandler):
    def initialize(self, info, template_name=None, template_path=None):
        self.info = info
        self.template_name = template_name
        self.template_path = template_path

    def get(self, template_name=None):
        if template_name is None:
            template_name = self.template_name
        loc = os.path.join(self.template_path, template_name)
        self.render(
            loc,
            databench_version=DATABENCH_VERSION,
            **self.info
        )
