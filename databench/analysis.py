"""Analysis module for Databench."""

from __future__ import absolute_import, unicode_literals, division

from . import utils
from .datastore import Datastore
import inspect
import logging
import random
import string
import tornado.gen
import wrapt

log = logging.getLogger(__name__)


class ActionHandler(object):
    """Databench action handler."""

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


def on(f):
    """Decorator for action handlers.

    The action name is inferred from the function name.

    This also decorates the method with `tornado.gen.coroutine` so that
    `~tornado.concurrent.Future` can be yielded.
    """
    action = f.__name__
    f.action = action

    @wrapt.decorator
    @tornado.gen.coroutine
    def _execute(wrapped, instance, args, kwargs):
        return wrapped(*args, **kwargs)

    return _execute(f)


def on_action(action):
    """Decorator for action handlers.

    :param str action: explicit action name

    This also decorates the method with `tornado.gen.coroutine` so that
    `~tornado.concurrent.Future` can be yielded.
    """
    @wrapt.decorator
    @tornado.gen.coroutine
    def _execute(wrapped, instance, args, kwargs):
        return wrapped(*args, **kwargs)

    _execute.action = action
    return _execute


class Analysis(object):
    """Databench's analysis class.

    This contains the analysis code. Every browser connection corresponds to
    an instance of this class.

    **Initialization**: All initializations should be done in
    :meth:`.connected`. Instance variables (which should be avoided in favor
    of state) should be initialized in the constructor. Some cleanup
    can be done in :meth:`.disconnected`.

    **Arguments/Parameters**: Command line arguments are available
    at ``cli_args`` and the parameters of the HTTP GET request at
    ``request_args``. ``request_args`` is a dictionary of all
    arguments. Each value of the dictionary is a list of given values for this
    key even if this key only appeared once in the url
    (see `urllib.parse.parse_qs`).

    **Actions**: are captured by class method decorated
    with `databench.on`. To capture the action
    ``run`` that is emitted with the JavaScript code

    .. code-block:: js

        // on the JavaScript frontend
        d.emit('run', {my_param: 'helloworld'});

    use

    .. code-block:: python

        # in Python
        @databench.on
        def run(self, my_param):
            pass

    in Python. Lists are treated as positional arguments and objects as keyword
    arguments to the function call.
    If the message is neither of type `list` nor `dict` (for example a
    plain `string` or `float`), the function will be called with that
    as its first parameter.

    **Writing to a datastore**: By default, a :class:`Datastore`
    scoped to the current analysis instance is created at
    ``data``. You can write state updates to it with

    .. code-block:: python

        yield self.set_state(key1=value1)

    Similarly, there is a :class:`Datastore` instance at
    ``class_data`` which is
    scoped to all instances of this analysis by its class name and state
    updates are supported with :meth:`.set_class_state`.

    **Communicating with the frontend**: The default is to change state with
    :meth:`.set_state` or :meth:`.set_class_state` and let that
    change propagate to all frontends. Directly calling :meth:`.emit` is also
    possible.

    :ivar Datastore data: data scoped for this instance/connection
    :ivar Datastore class_data: data scoped across all instances
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

        This creates instances of :class:`.Datastore` at ``data`` and
        ``class_data`` with the datastore domains being the current id
        and the class name of this analysis respectively.

        Overwrite this method to use other datastore backends.
        """
        self.data = Datastore(self.id_)
        self.data.subscribe(lambda data: self.emit('data', data))
        self.class_data = Datastore(type(self).__name__)
        self.class_data.subscribe(lambda data: self.emit('class_data', data))

    @staticmethod
    def __create_id():
        return ''.join(random.choice(string.ascii_letters + string.digits)
                       for _ in range(8))

    def set_emit_fn(self, emit_fn):
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

    @on
    def connect(self):
        pass

    @on
    def args(self, cli_args, request_args):
        self.cli_args = cli_args
        self.request_args = request_args

    @on
    def log(self, *args, **kwargs):
        self.log_frontend.info(utils.to_string(*args, **kwargs))

    @on
    def warn(self, *args, **kwargs):
        self.log_frontend.warn(utils.to_string(*args, **kwargs))

    @on
    def error(self, *args, **kwargs):
        self.log_frontend.error(utils.to_string(*args, **kwargs))

    @on
    def connected(self):
        """Default handler for "connected" action.

        Overwrite to add behavior.
        """
        pass

    @on
    def disconnected(self):
        """Default handler for "disconnected" action.

        Overwrite to add behavior.
        """
        log.debug('on_disconnected called.')

    @on
    def set_state(self, updater=None, **kwargs):
        """Set state in Datastore."""
        yield self.data.set_state(updater, **kwargs)

    @on
    def set_class_state(self, updater=None, **kwargs):
        """Set state in class Datastore."""
        yield self.class_data.set_state(updater, **kwargs)
