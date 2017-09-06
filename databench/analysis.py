"""Analysis module for Databench."""

from __future__ import absolute_import, unicode_literals, division

import inspect
import logging
import random
import string
import tornado.gen
import warnings

from . import utils
from .datastore_legacy import DatastoreLegacy

log = logging.getLogger(__name__)


class ActionHandler(object):
    def __init__(self, action, f, bound_instance=None):
        self.action = action
        self.f = f
        self.bound_instance = bound_instance

    @tornado.gen.coroutine
    def __call__(self, *args, **kwargs):
        if self.bound_instance is not None:
            return self.f(self.bound_instance, *args, **kwargs)

        return self.f(*args, **kwargs)

    def __get__(self, obj, objtype):
        if obj is not None:
            # return an ActionHandler that is bound to the given instance
            return ActionHandler(self.action, self.f, obj)

        return self

    def code(self):
        """Get the source code of the decorated function."""
        return inspect.getsource(self.f)


def on(action):
    """Decorator for action handlers.

    This also decorates the method with `tornado.gen.coroutine` so that
    `~tornado.concurrent.Future`s can be `yield`ed.

    The decorated object will have a :meth:`code` to retrieve its source code.

    The action name can be given explicitely or can be inferred from the
    function name.
    """
    if callable(action):
        f = action
        action = f.__name__
        return ActionHandler(action, f)

    def decorated_with_action_name(f):
        return ActionHandler(action, f)

    return decorated_with_action_name


class Analysis(object):
    """Databench's analysis class.

    This contains the analysis code. Every browser connection corresponds to
    an instance of this class.

    **Initialization**: All initializations should be done in
    :meth:`.on_connected`. Instance variables (which should be avoided in favor
    of `.data`) should be initialized in the constructor. Some cleanup
    can be done in :meth:`.on_disconnected`.

    **Arguments/Parameters**: Command line arguments are available
    at `.cli_args` and the parameters of the HTTP GET request at
    `.request_args`. `.request_args` is a dictionary of all
    arguments. Each value of the dictionary is a list of given values for this
    key even if this key only appeared once in the url
    (see `urllib.parse.parse_qs`).

    **Actions**: are captured by specifying a class method starting
    with ``on_`` followed by the action name. To capture the action
    ``run`` that is emitted with the JavaScript code

    .. code-block:: js

        // on the JavaScript frontend
        d.emit('run', {my_param: 'helloworld'});

    use

    .. code-block:: python

        # in Python
        def on_run(self, my_param):

    in Python. Lists are treated as positional arguments and objects as keyword
    arguments to the function call.
    If the message is neither of type `list` nor `dict` (for example a
    plain `string` or `float`), the function will be called with that
    as its first parameter.

    **Writing to a datastore**: By default, a :class:`.DatastoreLegacy` scoped
    to the current analysis instance is created at `.data`. You can write
    key-value pairs to it with

    .. code-block:: python

        self.data[key] = value

    Similarly, there is a `.class_data` :class:`.DatastoreLegacy` which is
    scoped to all instances of this analysis by its class name.

    **Communicating with the frontend**: The default is to change state by
    changing and entry in `.data` or `.class_data` and let that
    change propagate to the frontend. Directly calling :meth:`.emit` is also
    possible.

    **Outgoing messages**: changes to the datastore are emitted to the
    frontend and this path should usually not be modified. However, databench
    does provide access to :meth:`.emit`
    method and to methods that modify a value for a key before it is send
    out with ``data_<key>(value)`` methods.

    :ivar DatastoreLegacy data: data scoped for this instance/connection
    :ivar DatastoreLegacy class_data: data scoped across all instances
    :ivar list cli_args: command line arguments
    :ivar dict request_args: request arguments
    """

    _databench_analysis = True

    def __init__(self):
        self.data = None
        self.class_data = None
        self.cli_args = []
        self.request_args = {}

    def init_databench(self, id_=None):
        self.id_ = id_ if id_ else Analysis.__create_id()
        self.emit_to_frontend = (
            lambda s, pl:
                log.error('emit called before Analysis setup was complete')
        )
        self.log_frontend = logging.getLogger(__name__ + '.frontend')
        self.log_backend = logging.getLogger(__name__ + '.backend')

        self.init_datastores()
        return self

    def init_datastores(self):
        """Initialize datastores for this analysis instance.

        This creates instances of :class:`.Datastore` at `.data` and
        `.class_data` with the datastore domains being the current id
        and the class name of this analysis respectively.

        Overwrite this method to use other datastore backends.
        """
        self.data = DatastoreLegacy(self.id_)
        self.data.subscribe(self.data_change)
        self.class_data = DatastoreLegacy(type(self).__name__)
        self.class_data.subscribe(self.class_data_change)

    @staticmethod
    def __create_id():
        return ''.join(random.choice(string.ascii_letters + string.digits)
                       for _ in range(8))

    def set_emit_fn(self, emit_fn):
        """Sets what the emit function for this analysis will be."""
        self.emit_to_frontend = emit_fn
        return self

    def emit(self, signal, message='__nomessagetoken__'):
        """Emit a signal to the frontend.

        :param str signal: name of the signal
        :param message: message to send
        :returns: return value from frontend emit function
        :rtype: tornado.concurrent.Future
        """
        # call pre-emit hooks
        if signal == 'log':
            self.log_backend.info(message)
        elif signal == 'warn':
            self.log_backend.warn(message)
        elif signal == 'error':
            self.log_backend.error(message)

        return self.emit_to_frontend(signal, message)

    """Events."""

    def on_connect(self):
        log.debug('on_connect called.')

    def on_args(self, cli_args, request_args):
        self.cli_args = cli_args
        self.request_args = request_args

    def on_log(self, *args, **kwargs):
        self.log_frontend.info(utils.to_string(*args, **kwargs))

    def on_warn(self, *args, **kwargs):
        self.log_frontend.warn(utils.to_string(*args, **kwargs))

    def on_error(self, *args, **kwargs):
        self.log_frontend.error(utils.to_string(*args, **kwargs))

    def on_connected(self):
        """Default handlers for the "connected" action.

        Overwrite to add behavior.

        .. versionadded:: 0.7
            Previously, most of this functionality was in ``on_connect()``.
        """
        log.debug('on_connected called.')

    def on_disconnected(self):
        """Default handler for "disconnected" action.

        Overwrite to add behavior.
        """
        log.debug('on_disconnected called.')

    """Data callbacks."""

    def data_change(self, key, value):
        if hasattr(self, 'data_{}'.format(key)):
            warnings.warn('Do not use data callbacks anymore.',
                          category=DeprecationWarning)
            value = getattr(self, 'data_{}'.format(key))(value)
        self.emit('data', {key: value})

    def class_data_change(self, key, value):
        if hasattr(self, 'class_data_{}'.format(key)):
            warnings.warn('Do not use data callbacks anymore.',
                          category=DeprecationWarning)
            value = getattr(self, 'class_data_{}'.format(key))(value)
        self.emit('class_data', {key: value})
