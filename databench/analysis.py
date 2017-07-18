"""Analysis module for Databench."""

from __future__ import absolute_import, unicode_literals, division

import logging
import random
import string

from . import utils
from .datastore import Datastore

log = logging.getLogger(__name__)


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

    **Writing to a datastore**: By default, a :class:`.Datastore` scoped to
    the current analysis instance is created at `.data`. You can write
    key-value pairs to it with

    .. code-block:: python

        self.data[key] = value

    Similarly, there is a `.class_data` :class:`.Datastore` which is
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
    """

    _databench_analysis = True
    datastore_class = Datastore

    def __init__(self):
        #: Data specific to this instance of this analysis and therefore
        #: connection.
        self.data = None
        #: Data that is shared across all instances of this analysis.
        self.class_data = None
        #: Command line arguments.
        self.cli_args = []
        #: Request arguments.
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
        self.data = Analysis.datastore_class(self.id_)
        self.data.on_change(self.data_change)
        self.class_data = Analysis.datastore_class(type(self).__name__)
        self.class_data.on_change(self.class_data_change)

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
            value = getattr(self, 'data_{}'.format(key))(value)
        self.emit('data', {key: value})

    def class_data_change(self, key, value):
        if hasattr(self, 'class_data_{}'.format(key)):
            value = getattr(self, 'class_data_{}'.format(key))(value)
        self.emit('class_data', {key: value})
