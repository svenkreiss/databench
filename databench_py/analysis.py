"""Analysis module for Databench Python kernel."""

from databench import DatastoreLegacy
from databench import utils
import logging

log = logging.getLogger(__name__)


class Analysis(object):
    """Databench's analysis class."""

    _databench_analysis = True

    def __init__(self):
        pass

    def init_databench(self, id_):
        self.id_ = id_
        self.emit = lambda s, pl: log.error('emit called before Analysis '
                                            'setup complete')

        self.init_datastores()
        return self

    def init_datastores(self):
        self.data = DatastoreLegacy(self.id_)
        self.data.subscribe(self.data_change)
        self.class_data = DatastoreLegacy(type(self).__name__)
        self.class_data.subscribe(self.class_data_change)

    def set_emit_fn(self, emit_fn):
        """Sets what the emit function for this analysis will be."""
        self.emit = emit_fn
        return self

    """Events."""

    def on_connect(self):
        log.debug('on_connect called.')

    def on_args(self, cli_args, request_args):
        self.cli_args = cli_args
        self.request_args = request_args

    def on_log(self, *args, **kwargs):
        log.info(utils.to_string(*args, **kwargs))

    def on_warn(self, *args, **kwargs):
        log.warn(utils.to_string(*args, **kwargs))

    def on_error(self, *args, **kwargs):
        log.error(utils.to_string(*args, **kwargs))

    def on_connected(self):
        log.debug('on_connected called.')

    def on_disconnected(self):
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
