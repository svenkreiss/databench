"""Analysis module for Databench."""

from __future__ import absolute_import, unicode_literals, division

import logging
import random
import string

from .datastore import Datastore

log = logging.getLogger(__name__)


class Analysis(object):
    """Databench's analysis class.

    This contains the analysis code. Every browser connection corresponds to
    and instance of this class.

    **Initialize:** add an ``on_connect(self)`` method to your analysis class.

    **Request args:** ``request_args`` or GET parameters are processed with a
    ``on_request_args(argv)`` method where ``argv`` is a dictionary of all
    arguments. Each value of the dictionary is a list of given values for this
    key even if this key only appeared once in the url.

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
    frontend and this path should usually not be modified. However, databench
    does provide access to ``emit()``
    method and to methods that modify a value for a key before it is send
    out with ``data_<key>(value)`` methods.
    """

    _databench_analysis = True

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
