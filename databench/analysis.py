"""Analysis module for Databench."""

import os
import json
import logging
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

    def __init__(self):
        pass

    def set_emit_fn(self, emit_fn):
        """Sets what the emit function for this analysis will be."""
        self.emit = emit_fn

    """Events."""

    def onall(self, message_data):
        log.debug('onall called.')

    def on_connect(self):
        log.debug('on_connect called.')

    def on_disconnect(self):
        log.debug('on_disconnect called.')


class Meta(object):
    """
    Args:
        name (str): Name of this analysis. If ``signals`` is not specified,
            this also becomes the namespace for the WebSocket connection and
            has to match the frontend's :js:class:`Databench` ``name``.
        import_name (str): Usually the file name ``__name__`` where this
            analysis is instantiated.
        description (str): Usually the ``__doc__`` string of the analysis.
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

    def __init__(
            self,
            name,
            import_name,
            description,
            analysis_class,
    ):
        Meta.all_instances.append(self)
        self.show_in_index = True
        self.name = name

        # find folder of all analyses
        analyses_path = os.path.join(os.getcwd(), 'analyses')
        if not os.path.exists(analyses_path):
            analyses_path = os.path.join(
                os.getcwd(), 'databench', 'analyses_packaged',
            )
        if not os.path.exists(analyses_path):
            log.info('Folder for {} not found.'.format(self.name))
        # find folder for this analysis
        analysis_path = os.path.join(analyses_path, self.name)

        self.info = {'logo_url': '/static/logo.svg', 'title': 'Databench'}
        self.description = description
        self.analysis_class = analysis_class

        self.routes = [
            (r'/{}/static/(.*)'.format(self.name),
             tornado.web.StaticFileHandler,
             {'path': analysis_path}),

            (r'/{}/ws'.format(self.name),
             FrontendHandler,
             {'instantiate_analysis': self.instantiate_analysis_class}),

            (r'/{}/(?P<template_name>.+\.html)'.format(self.name),
             RenderTemplate,
             {'template_path': analysis_path,
              'info': self.info}),

            (r'/{}/'.format(self.name),
             RenderTemplate,
             {'template_name': 'index.html',
              'template_path': analysis_path,
              'info': self.info}),
        ]

        # detect whether thumbnail.png is present
        thumbnail_path = os.path.join(analysis_path, 'thumbnail.png')
        if os.path.isfile(thumbnail_path):
            self.thumbnail = 'thumbnail.png'

        self.request_args = None

    def instantiate_analysis_class(self):
        return self.analysis_class()

    @staticmethod
    def run_action(analysis, fn_name, message):
        """Executes an action in the analysis with the given message. It
        also handles the start and stop signals in case an action_id
        is given."""

        # detect action_id
        action_id = None
        if isinstance(message, dict) and '__action_id' in message:
            action_id = message['__action_id']
            del message['__action_id']

        if action_id:
            analysis.emit('__action', {'id': action_id, 'status': 'start'})

        fn = getattr(analysis, fn_name)

        # Check whether this is a list (positional arguments)
        # or a dictionary (keyword arguments).
        if isinstance(message, list):
            fn(*message)
        elif isinstance(message, dict):
            fn(**message)
        else:
            fn(message)

        if action_id:
            analysis.emit('__action', {'id': action_id, 'status': 'end'})


class FrontendHandler(tornado.websocket.WebSocketHandler):
    @staticmethod
    def sanitize_message(m):
        try:
            if m != m:
                m = 'NaN'
            elif m == float('inf'):
                m = 'inf'
            elif m == float('-inf'):
                m = '-inf'
            elif isinstance(m, list):
                for i in range(len(m)):
                    m[i] = FrontendHandler.sanitize_message(m[i])
            elif isinstance(m, dict):
                for i in m.iterkeys():
                    m[i] = FrontendHandler.sanitize_message(m[i])
        except:
            # Some types cannot be compared (like numpy arrays).
            # Just skip those.
            return m
        return m

    def initialize(self, instantiate_analysis):
        self.instantiate_analysis = instantiate_analysis
        self.analysis_instance = None

    def open(self):
        log.debug('WebSocket connection opened.')
        self.analysis_instance = self.instantiate_analysis()
        self.analysis_instance.set_emit_fn(self.emit)
        log.debug("analysis instantiated")
        self.analysis_instance.on_connect()

    def on_close(self):
        log.debug('WebSocket connection closed.')
        self.analysis_instance.on_disconnect()

    def on_message(self, message):
        if message is None:
            log.debug('empty message received.')
            return

        message_data = json.loads(message)
        self.analysis_instance.onall(message_data)
        if 'signal' not in message_data or 'load' not in message_data:
            log.info('message not processed: '+message)
            return

        fn_name = 'on_'+message_data['signal']
        if not hasattr(self.analysis_instance, fn_name):
            log.warning('frontend wants to call '+fn_name +
                        ' which is not in the Analysis class.')
            return

        log.debug('calling '+fn_name)
        Meta.run_action(
            self.analysis_instance,
            fn_name,
            message_data['load'],
        )

    def emit(self, signal, message):
        message = FrontendHandler.sanitize_message(message)
        try:
            self.write_message(json.dumps(
                {'signal': signal, 'load': message}
            ).encode('utf-8'))
        except tornado.websocket.WebSocketClosedError:
            pass
            # log.error('WebSocket is closed. Cannot emit message: {}'
            #           ''.format(message))


class RenderTemplate(tornado.web.RequestHandler):
    def initialize(self, template_name, template_path, info):
        self.template_loc = os.path.join(template_path, template_name)
        self.info = info

    def get(self):
        self.render(
            self.template_loc,
            info=self.info,
            databench_version=DATABENCH_VERSION,
        )
