"""Analysis module for Databench Python kernel."""

import logging


class Analysis(object):
    """Databench's analysis class."""

    def __init__(self):
        pass

    def set_emit_fn(self, emit_fn):
        """Sets what the emit function for this analysis will be."""
        self.emit = emit_fn

    """Events."""

    def on_connect(self):
        logging.debug('on_connect called.')

    def on_disconnect(self):
        logging.debug('on_disconnect called.')
