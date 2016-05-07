from collections import defaultdict
import copy
import logging

log = logging.getLogger(__name__)


class Datastore(object):
    """key-value data store

    An in-memory and in-process (not persistent) key-value store. It behaves in
    many ways like a dictionary.

    :param domain:
        A namespace for the key values. This can be an analysis instance id for
        data local to an analysis instance or the name of an analysis class
        for data that is shared across instances of the same analysis.
    """
    store = defaultdict(dict)
    on_change_cb = defaultdict(list)

    def __init__(self, domain):
        self.domain = domain

    def on_change(self, callback):
        """register a change callback

        :param callback:
            A callback function that takes in a key and a value.
        """
        Datastore.on_change_cb[self.domain].append(callback)
        return self

    def __setitem__(self, key, value):
        """set value for given key

        Allows for assignments of the form ``d[key] = value``. The value is
        copied using ``copy.deepcopy(value)`` before it is stored. Callbacks
        are skipped if the value is already assigned to the key.
        """
        if key in Datastore.store[self.domain] and \
           Datastore.store[self.domain][key] == value:
            return self

        value = copy.deepcopy(value)

        Datastore.store[self.domain][key] = value
        for cb in Datastore.on_change_cb[self.domain]:
            cb(key, value)

        return self

    def __getitem__(self, key):
        """return the value for the given key"""
        return Datastore.store[self.domain][key]

    def __contains__(self, key):
        """test whether key is set"""
        return key in Datastore.store[self.domain]

    def update(self, key_value_pairs):
        """Similar to ``dict.update()``.

        :param dict key_value_pairs:
            A dictionary of key value pairs to update.
        """
        for k, v in key_value_pairs.items():
            self[k] = v

    def init(self, key_value_pairs):
        """initialize datastore

        Only sets values for keys that are not in the datastore already.
        No callbacks are called.

        :param dict key_value_pairs:
            A set of key value pairs to use to initialize the datastore.
        """
        for k, v in key_value_pairs.items():
            if k not in Datastore.store[self.domain]:
                Datastore.store[self.domain][k] = copy.deepcopy(v)
