"""Analysis module for Databench."""

from __future__ import absolute_import, unicode_literals, division

import json
import logging
import os
import random
import string
import sys
import tornado.gen
import tornado.web
import tornado.websocket

from . import __version__ as DATABENCH_VERSION
from .datastore import Datastore
from .readme import Readme

log = logging.getLogger(__name__)


class Analysis(object):
    """Databench's analysis class.

    This contains the analysis code. Every browser connection corresponds to
    and instance of this class.

    **Initialize:** add an ``on_connect(self)`` or
    ``on_connect(self, request_args)`` method to your analysis class. The
    optional argument ``request_args`` contains a dictionary of parameters
    from the request url.

    **Actions:** are captured by specifying a class method starting
    with ``on_`` followed by the action name. To capture the action
    ``run`` that is emitted with the JavaScript code

    .. code-block:: js

        // on the JavaScript frontend
        d.emit('run', {my_param: 'helloworld'});

    use

    .. code-block:: python

        # here in Python
        def on_run(self, my_param):

    here. The entries of a dictionary will be used as keyword arguments in the
    function call. If the emitted message is an array,
    the entries will be used as positional arguments in the function call.
    If the message is neither of type ``list`` nor ``dict`` (for example a
    plain ``string`` or ``float``), the function will be called with that
    as its first parameter.

    **Writing to a datastore:** By default, a :class:`Datastore` scoped to
    the current analysis instance is created at ``self.data``. You can write
    key-value pairs to it with

    .. code-block:: python

        self.data[key] = value

    Similarly, there is a ``self.class_data`` :class:`Datastore` which is
    scoped to all instances of this analysis by its class name.

    **Outgoing messages**: changes to the datastore are emitted to the
    frontend and this path should usually not be modified (according to the
    Flux model). However, databench does provide access to ``emit()``
    method and to methods that modify a value for a key before it is send
    out with ``data_<key>(value)`` methods.
    """

    def __init__(self, id_=None):
        self.id_ = id_ if id_ else Analysis.__create_id()
        self.emit = lambda s, pl: log.error('emit called before Analysis '
                                            'setup complete')
        self.init_datastores()

    def init_datastores(self):
        """Initialize datastores for this analysis instance.

        This creates instances of :class:`Datastore` at ``self.data`` and
        ``seld.class_data`` with the datastore domains being the current id
        and the class name of this analysis respectively.

        Overwrite this method to use other datastore backends.
        """
        self.data = Datastore(self.id_)
        self.data.on_change(self.data_change)
        self.class_data = Datastore(type(self).__name__)
        self.class_data.on_change(self.class_data_change)

    @staticmethod
    def __create_id():
        return ''.join(random.choice(string.ascii_letters + string.digits)
                       for _ in range(8))

    def set_emit_fn(self, emit_fn):
        """Sets what the emit function for this analysis will be."""
        self.emit = emit_fn
        return self

    """Events."""

    def on_connect(self):
        """Default handlers for the "connect" action.

        Overwrite to add behavior.
        """
        log.debug('on_connect called.')

    def on_disconnected(self):
        """Default handler for "disconnected" action.

        Overwrite to add behavior.
        """
        log.debug('on_disconnected called.')

    """Data callbacks."""

    def data_change(self, key, value):
        if hasattr(self, 'data_{}'.format(key)):
            value = getattr(self, 'data_{}'.format(key))(value)
        self.emit('data', {key: value})

    def class_data_change(self, key, value):
        if hasattr(self, 'class_data_{}'.format(key)):
            value = getattr(self, 'class_data_{}'.format(key))(value)
        self.emit('class_data', {key: value})


class Meta(object):
    """Meta class referencing an analysis.

    An instance of this class is created in every ``analysis.py``.

    :param str name:
        Name of this analysis. If ``signals`` is not specified,
        this also becomes the namespace for the WebSocket connection and
        has to match the frontend's :js:class:`Databench` ``name``.

    :param analysis_class:
        Object that should be instantiated for every new websocket connection.
    :type analysis_class: :class:`databench.Analysis`
    """

    def __init__(self, name, analysis_class):
        self.name = name
        self.analysis_class = analysis_class
        self.show_in_index = True
        self.request_args = None

        self._analysis_path = None
        self._info = None
        self._routes = None
        self._thumbnail = None

    @property
    def analysis_path(self):
        if self._analysis_path is None:
            if os.path.isfile('analyses/__init__.py'):
                sys.path.append('.')
                import analyses
            else:
                log.debug('Did not find analyses. Using packaged analyses.')
                from . import analyses_packaged as analyses
            analyses_path = os.path.dirname(
                os.path.realpath(analyses.__file__)
            )
            self._analysis_path = os.path.join(analyses_path, self.name)

        return self._analysis_path

    @property
    def info(self):
        if self._info is None:
            readme = Readme(self.analysis_path)
            self._info = {
                'title': self.name,
                'description': '',
                'readme': readme.text,
            }
            self._info.update(readme.meta)

        return self._info

    @property
    def routes(self):
        if self._routes is None:
            self._routes = [
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
            ]
        return self._routes

    @property
    def thumbnail(self):
        if self._thumbnail is None:
            # detect whether thumbnail.png is present
            if os.path.isfile(os.path.join(self.analysis_path,
                                           'thumbnail.png')):
                self._thumbnail = 'thumbnail.png'
            else:
                self._thumbnail = False
        return self._thumbnail

    @tornado.gen.coroutine
    def run_process(self, analysis, action_name, message='__nomessagetoken__'):
        """Executes an action in the analysis with the given message.

        It also handles the start and stop signals in case a process_id
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
        tornado.autoreload.add_reload_hook(self.on_close)

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
            return

        if self.analysis is None:
            log.warning('no analysis connected. Abort.')
            return

        if 'signal' not in msg or 'load' not in msg:
            log.info('message not processed: {}'.format(message))
            return

        self.meta.run_process(self.analysis, msg['signal'], msg['load'])

    def emit(self, signal, message):
        message = sanitize_message(message)
        try:
            self.write_message(json.dumps(
                {'signal': signal, 'load': message}
            ).encode('utf-8'))
        except tornado.websocket.WebSocketClosedError:
            pass


def sanitize_message(m):
    if isinstance(m, int) or isinstance(m, float):
        if m != m:
            m = 'NaN'
        elif m == float('inf'):
            m = 'inf'
        elif m == float('-inf'):
            m = '-inf'
    elif isinstance(m, list):
        for i, e in enumerate(m):
            m[i] = sanitize_message(e)
    elif isinstance(m, dict):
        for i in m:
            m[i] = sanitize_message(m[i])
    elif isinstance(m, (set, tuple)):
        m = [sanitize_message(e) for e in m]
    elif hasattr(m, 'tolist'):  # for np.array
        m = [sanitize_message(e) for e in m]
    return m


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
