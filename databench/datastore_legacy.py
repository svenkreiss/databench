from .utils import json_encoder_default
from collections import defaultdict
from future.builtins import zip
import json
import logging

log = logging.getLogger(__name__)


def decode(value):
    if isinstance(value, DatastoreList):
        return value
    elif isinstance(value, DatastoreDict):
        return value

    return json.loads(value)


def encode(value, callback):
    if isinstance(value, list):
        return DatastoreList(value, callback)
    elif isinstance(value, dict):
        return DatastoreDict(value, callback)
    elif isinstance(value, DatastoreList):
        value._change_callback = callback
        return value
    elif isinstance(value, DatastoreDict):
        value._change_callback = callback
        return value

    return json.dumps(value, default=json_encoder_default)


class DatastoreList(object):
    """Object wrapper for storing a list in Datastore.

    This triggers callbacks when elements are modified.
    """
    def __init__(self, data, callback):
        self._change_callback = callback
        self.data = [encode(v, self.get_change_trigger(i))
                     for i, v in enumerate(data)]

    def trigger_changed(self, i):
        return self._change_callback(i)

    def get_change_trigger(self, i):
        return lambda _: self.trigger_changed(i)

    def __iter__(self):
        """List iterator."""
        return (decode(v) for v in self.data)

    def __getitem__(self, i):
        """Get item."""
        return decode(self.data[i])

    def set(self, i, value):
        """Set value at position i and return a Future.

        :rtype: tornado.concurrent.Future
        """
        value_encoded = encode(value, self.get_change_trigger(i))

        if i in self.data and self.data[i] == value_encoded:
            return self

        self.data[i] = value_encoded
        return self.trigger_changed(i)

    def __setitem__(self, i, value):
        """Set value at position i."""
        self.set(i, value)
        return self

    def __eq__(self, other):
        if not isinstance(other, DatastoreList):
            return False

        return (len(self) == len(other) and
                all(v1 == v2 for v1, v2 in zip(self.data, other.data)))

    def __len__(self):
        return len(self.data)

    def to_native(self):
        """Convert to a Python list."""
        return [v.to_native() if hasattr(v, 'to_native') else v for v in self]


class DatastoreDict(object):
    """Object wrapper for storing a dict in Datastore.

    :param change_callback: callback whithout arguments

    This trigger then change callback when elements are modified.
    """
    def __init__(self, data=None, change_callback=None):
        if data is None:
            data = {}
        if change_callback is None:
            change_callback = lambda k: None

        self._change_callback = change_callback
        self.data = {k: encode(v, self.get_change_trigger(k))
                     for k, v in data.items()}

    def trigger_changed(self, key):
        return self._change_callback(key)

    def get_change_trigger(self, key):
        return lambda _: self.trigger_changed(key)

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

    def get_encoded(self, key):
        if key not in self.data:
            raise IndexError
        return self.data[key]

    def set(self, key, value):
        """Set a value at key and return a Future.

        :rtype: tornado.concurrent.Future
        """
        value_encoded = encode(value, self.get_change_trigger(key))

        if key in self.data and self.data[key] == value_encoded:
            return self

        self.data[key] = value_encoded
        return self.trigger_changed(key)

    def __setitem__(self, key, value):
        """Set a value at key."""
        self.set(key, value)
        return self

    def __eq__(self, other):
        if not isinstance(other, DatastoreDict):
            return False

        keys = set(self.data.keys()) & set(other.data.keys())
        return (len(self) == len(other) == len(keys) and
                all(self.data[k] == other.data[k] for k in keys))

    def __len__(self):
        """Length of the dictionary."""
        return len(self.data)

    def __iter__(self):
        """Iterator."""
        return (k for k in self.data.keys())

    def __contains__(self, key):
        """Test whether key is set."""
        return key in self.data

    def __delitem__(self, key):
        """Delete the given key."""
        del self.data[key]
        self.trigger_changed(key)

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

    def update(self, new_data):
        """Update."""
        for k, v in new_data.items():
            self[k] = v

        return self

    def to_native(self):
        return {k: v.to_native() if hasattr(v, 'to_native') else v
                for k, v in self.items()}


class DatastoreLegacy(object):
    """Key-value data store.

    An in-memory and in-process (not persistent) key-value store.

    :param domain:
        A namespace for the key values. This can be an analysis instance id for
        data local to an analysis instance or the name of an analysis class
        for data that is shared across instances of the same analysis.

    :param bool release_storage:
        Release storage when the last datastore for a domain closes.
    """
    store = defaultdict(DatastoreDict)
    datastores = defaultdict(list)  # list of instances by domain

    def __init__(self, domain, release_storage=False):
        self.domain = domain
        self.release_storage = release_storage
        self.change_callbacks = []
        datastore_dict = DatastoreLegacy.store[self.domain]
        datastore_dict._change_callback = self.trigger_change_callbacks
        DatastoreLegacy.datastores[self.domain].append(self)

    def on_change(self, callback):
        """Subscribe to changes in the datastore with a callback.

        Deprecated. Use :meth:`subscribe` instead.

        :param callback: Function that takes in a key and a value.
        """
        self.change_callbacks.append(callback)
        return self

    def subscribe(self, callback):
        """Subscribe to changes in the datastore with a callback.

        :param callback: Function that takes in a key and a value.
        """
        self.change_callbacks.append(callback)
        return self

    def trigger_change_callbacks(self, key):
        value = DatastoreLegacy.store[self.domain].get(key, None)
        return [
            callback(key, value)
            for datastore in DatastoreLegacy.datastores[self.domain]
            for callback in datastore.change_callbacks
        ]

    def trigger_all_change_callbacks(self):
        """Trigger all callbacks that were set with on_change()."""
        return [
            ret
            for key in DatastoreLegacy.store[self.domain].keys()
            for ret in self.trigger_change_callbacks(key)
        ]

    def set(self, key, value):
        """Set value at key and return a Future

        :rtype: tornado.concurrent.Future
        """
        return DatastoreLegacy.store[self.domain].set(key, value)

    def __setitem__(self, key, value):
        """Set value for given key.

        Allows for assignments of the form ``d[key] = value``.
        Callbacks are skipped if the json-encoded value is unchanged.
        """
        self.set(key, value)
        return self

    def __getitem__(self, key):
        """Return the value for the given key."""
        return DatastoreLegacy.store[self.domain][key]

    def __delitem__(self, key):
        """Delete the given key."""
        del DatastoreLegacy.store[self.domain][key]
        self.trigger_change_callbacks(key)

    def __contains__(self, key):
        """Test whether key is set."""
        return key in DatastoreLegacy.store[self.domain]

    def update(self, key_value_pairs):
        """Similar to :meth:`dict.update`.

        :param dict key_value_pairs:
            A dictionary of key value pairs to update.
        """
        DatastoreLegacy.store[self.domain].update(key_value_pairs)

    def init(self, key_value_pairs):
        """Initialize datastore.

        Only sets values for keys that are not in the datastore already.

        :param dict key_value_pairs:
            A set of key value pairs to use to initialize the datastore.
        """
        for k, v in key_value_pairs.items():
            if k not in DatastoreLegacy.store[self.domain]:
                DatastoreLegacy.store[self.domain][k] = v

    def close(self):
        """Close and delete instance."""

        # remove callbacks
        DatastoreLegacy.datastores[self.domain].remove(self)

        # delete data after the last instance is gone
        if self.release_storage and \
           not DatastoreLegacy.datastores[self.domain]:
            del DatastoreLegacy.store[self.domain]

        del self
