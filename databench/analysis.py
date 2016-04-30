"""Analysis module for Databench."""

from __future__ import absolute_import, unicode_literals, division

from .datastore import Datastore
from .readme import Readme
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

log = logging.getLogger(__name__)


class Analysis(object):
    """Databench's analysis class.

    This contains the analysis code. Every browser connection corresponds to
    and instance of this class.

    **Initialize:** add an ``on_connect(self)`` or
    ``on_connect(self, request_args)`` method to your analysis class. The
    optional argument ``request_args`` contains a dictionary of parameters
    from the request url.

    **Incoming messages** are captured by specifying a class method starting
    with ``on_`` followed by the signal name. To capture the frontend signal
    ``run`` that is emitted with the JavaScript code

    .. code-block:: js

        // on the JavaScript frontend
        databench.emit('run', {my_param: 'helloworld'});

    use

    .. code-block:: python

        # here in Python
        def on_run(self, my_param):

    here. The entries of a dictionary will be used as keyword arguments in the
    function call; as in this example. If the emitted message is an array,
    the entries will be used as positional arguments in the function call.
    If the message is neither of type ``list`` nor ``dict`` (for example a
    plain ``string`` or ``float``), the function will be called with that
    as its first parameter.

    **Outgoing messages** are sent using ``emit(signal_name, message)``.
    For example, use

    .. code-block:: python

        self.emit('result', {'msg': 'done'})

    to send the signal ``result`` with the message ``{'msg': 'done'}`` to
    the frontend.

    """

    datastore_class = Datastore

    def __init__(self, id_=None):
        self.id_ = id_ if id_ else Analysis.__create_id()
        self.emit = lambda s, pl: log.error('emit called before Analysis '
                                            'setup complete')

        self.data = Analysis.datastore_class(self.id_)
        self.global_data = Analysis.datastore_class(type(self).__name__)

        self.data.on_change(self._data_change)
        self.global_data.on_change(self._global_data_change)

    def _data_change(self, key, value):
        self.data_change(key, value)
        if hasattr(self, 'data_{}'.format(key)):
            getattr(self, 'data_{}'.format(key))(value)

    def _global_data_change(self, key, value):
        self.global_data_change(key, value)
        if hasattr(self, 'global_data_{}'.format(key)):
            getattr(self, 'global_data_{}'.format(key))(value)

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
        log.debug('on_connect called.')

    def on_disconnect(self):
        log.debug('on_disconnect called.')

    def on_data(self, **kwargs):
        self.data.update(kwargs)

    def on_global_data(self, **kwargs):
        self.global_data.update(kwargs)

    """Data callbacks."""

    def data_change(self, key, value):
        self.emit('data', {key: value})

    def global_data_change(self, key, value):
        self.emit('global_data', {key: value})


class Meta(object):
    """Meta class referencing an analysis.

    Args:
        name (str): Name of this analysis. If ``signals`` is not specified,
            this also becomes the namespace for the WebSocket connection and
            has to match the frontend's :js:class:`Databench` ``name``.
        description (str): Defined in README.
        analysis_class (:class:`databench.Analysis`): Object
            that should be instantiated for every new websocket connection.

    For standard use cases, you don't have to modify this class. However,
    If you want to serve more than the ``index.html`` page, say a
    ``details.html`` page, you can derive from this class and add this
    to the constructor

    .. code-block:: python

        self.blueprint.add_url_rule('/details.html', 'render_details',
                                    self.render_details)

    and add a new method to the class

    .. code-block:: python

        def render_details(self):
            return render_template(
                self.name+'/details.html',
                analysis_description=self.description
            )

    and create the file ``details.html`` similar to ``index.html``.

    """

    all_instances = []

    def __init__(self, name, analysis_class):
        Meta.all_instances.append(self)
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
            sys.path.append('.')
            try:
                import analyses
            except ImportError:
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
    def run_action(self, analysis, fn_name, message='__nomessagetoken__'):
        """Executes an action in the analysis with the given message.

        It also handles the start and stop signals in case an action_id
        is given.
        """

        if analysis is None:
            return

        if not hasattr(analysis, fn_name):
            log.warning('Frontend wants to call {} which is not in the '
                        'Analysis class {}.'.format(fn_name, analysis))
            return

        # detect action_id
        action_id = None
        if isinstance(message, dict) and '__action_id' in message:
            action_id = message['__action_id']
            del message['__action_id']

        if action_id:
            analysis.emit('__action', {'id': action_id, 'status': 'start'})

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

        if action_id:
            analysis.emit('__action', {'id': action_id, 'status': 'end'})


class FrontendHandler(tornado.websocket.WebSocketHandler):

    def initialize(self, meta):
        self.meta = meta
        self.analysis = None
        tornado.autoreload.add_reload_hook(self.on_close)

    def open(self):
        log.debug('WebSocket connection opened.')

    def on_close(self):
        log.debug('WebSocket connection closed.')
        self.meta.run_action(self.analysis, 'on_disconnect')

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

            self.meta.run_action(self.analysis, 'on_connect')
            log.info('Connected to analysis.')
            return

        if self.analysis is None:
            log.warning('no analysis connected. Abort.')
            return

        if 'signal' not in msg or 'load' not in msg:
            log.info('message not processed: {}'.format(message))
            return

        fn_name = 'on_{}'.format(msg['signal'])
        self.meta.run_action(self.analysis, fn_name, msg['load'])

    def emit(self, signal, message):
        message = FrontendHandler.sanitize_message(message)
        # log.debug('websocket writing: {}'.format(message))
        try:
            self.write_message(json.dumps(
                {'signal': signal, 'load': message}
            ).encode('utf-8'))
        except tornado.websocket.WebSocketClosedError:
            pass
            # log.warning('WebSocket is closed. Cannot emit message: {}'
            #             ''.format(message))

    @staticmethod
    def sanitize_message(m):
        if isinstance(m, int) or isinstance(m, float):
            if m != m:
                m = 'NaN'
            elif isinstance(m, float) and m != m:
                m = 'NaN'
            elif m == float('inf'):
                m = 'inf'
            elif m == float('-inf'):
                m = '-inf'
        elif isinstance(m, list):
            for i, e in enumerate(m):
                m[i] = FrontendHandler.sanitize_message(e)
        elif isinstance(m, dict):
            for i in m:
                m[i] = FrontendHandler.sanitize_message(m[i])
        elif isinstance(m, (set, tuple)):
            m = list(m)
            for i, e in enumerate(m):
                m[i] = FrontendHandler.sanitize_message(e)
        elif hasattr(m, 'tolist'):  # for np.ndarray, np.generic
            m = m.tolist()
            for i, e in enumerate(m):
                m[i] = FrontendHandler.sanitize_message(e)
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
