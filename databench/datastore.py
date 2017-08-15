from .utils import json_encoder_default
from collections import defaultdict
import json
import logging

log = logging.getLogger(__name__)


def decode(value):
    return json.loads(value)


def encode(value):
    return json.dumps(value, default=json_encoder_default)


class Datastore(object):
    """Key-value data store.

    An in-memory and in-process (not persistent) key-value store.

    :param domain:
        A namespace for the key values. This can be an analysis instance id for
        data local to an analysis instance or the name of an analysis class
        for data that is shared across instances of the same analysis.

    :param bool release_storage:
        Release storage when the last datastore for a domain closes.
    """
    global_data = defaultdict(dict)  # the actual stored data
    stores = defaultdict(list)  # list of instances by domain

    def __init__(self, domain, release_storage=False):
        self.domain = domain
        self.release_storage = release_storage
        self.change_callbacks = []
        Datastore.stores[self.domain].append(self)

    @property
    def data(self):
        return Datastore.global_data[self.domain]

    def on_change(self, callback):
        """Register a change callback.

        :param callback: Function with signature (key, value) => None.
        """
        self.change_callbacks.append(callback)
        return self

    def trigger_change_callbacks(self, key):
        value = self.get(key)
        return [callback(key, value)
                for datastore in Datastore.stores[self.domain]
                for callback in datastore.change_callbacks]

    def trigger_all_change_callbacks(self):
        """Trigger all callbacks that were set with on_change()."""
        return [ret
                for key in self
                for ret in self.trigger_change_callbacks(key)]

    def get_encoded(self, key):
        if key not in self.data:
            raise IndexError
        return self.data[key]

    def __getitem__(self, key):
        """Return entry at key."""
        if key not in self.data:
            raise IndexError
        return decode(self.data[key])

    def get(self, key, default=None):
        """Return entry at key.

        Return a default value if the key is not present.
        """
        if key not in self.data:
            return default
        return decode(self.data[key])

    def set(self, key, value):
        """Set a value at key and return a Future.

        :rtype: tornado.concurrent.Future
        """
        value_encoded = encode(value)

        if key in self.data and self.data[key] == value_encoded:
            return self

        self.data[key] = value_encoded
        return self.trigger_change_callbacks(key)

    def set_state(self, updater):
        """Update the datastore.

        :param func|dict updater: (state) => state_change or dict state_change
        """
        if callable(updater):
            value = updater(self)
        else:
            value = updater

        return self.update(value)

    def __contains__(self, key):
        """Test whether key is set."""
        return key in self.data

    def init(self, key_value_pairs):
        """Initialize datastore.

        Only sets values for keys that are not in the datastore already.

        :param dict key_value_pairs:
            A set of key value pairs to use to initialize the datastore.

        :rtype: databench.Datastore
        """
        return [self.set(k, v)
                for k, v in key_value_pairs.items()
                if k not in self]

    def close(self):
        """Close and delete instance."""

        # remove callbacks
        Datastore.stores[self.domain].remove(self)

        # delete data after the last instance is gone
        if self.release_storage and not Datastore.stores[self.domain]:
            del Datastore.global_data[self.domain]

        del self

    def __len__(self):
        """Length of the dictionary."""
        return len(self.data)

    def __iter__(self):
        """Iterator."""
        return (k for k in self.data.keys())

    def __delitem__(self, key):
        """Delete the given key."""
        if key not in self.data:
            raise IndexError

        del self.data[key]
        self.trigger_change_callbacks(key)

    def __repr__(self):
        """repr"""
        return {k: self[k] for k in self}.__repr__()

    def keys(self):
        """Keys."""
        return self.data.keys()

    def values(self):
        """Values."""
        return (self[k] for k in self)

    def items(self):
        """Items."""
        return ((k, self[k]) for k in self)

    def update(self, key_value_pairs):
        """Similar to :meth:`dict.update`.

        :param dict key_value_pairs:
            A dictionary of key value pairs to update.
        """
        return [self.set(k, v) for k, v in key_value_pairs.items()]
