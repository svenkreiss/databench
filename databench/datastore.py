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
        self.data = [encode(v, self.trigger_changed) for v in data]

    def trigger_changed(self, key):
        self._change_callback(key)

    def __getitem__(self, key):
        return decode(self.data[key])

    def __setitem__(self, key, value):
        value_encoded = encode(value, self.trigger_changed)

        if key in self.data and self.data[key] == value_encoded:
            return self

        self.data[key] = value_encoded
        self.trigger_changed(key)

        return self

    def __eq__(self, other):
        if not isinstance(other, DatastoreList):
            return False

        return (len(self) == len(other) and
                all(v1 == v2 for v1, v2 in zip(self.data, other.data)))

    def __len__(self):
        return len(self.data)


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
        self.data = {k: encode(v, self.trigger_changed)
                     for k, v in data.items()}

    def trigger_changed(self, key):
        self._change_callback(key)

    def __getitem__(self, key):
        if key not in self.data:
            raise IndexError
        return decode(self.data[key])

    def get(self, key, default=None):
        if key not in self.data:
            return default
        return decode(self.data[key])

    def get_encoded(self, key):
        if key not in self.data:
            raise IndexError
        return self.data[key]

    def __setitem__(self, key, value):
        value_encoded = encode(value, self.trigger_changed)
        print(key, value, value_encoded)

        if key in self.data and self.data[key] == value_encoded:
            return self

        self.data[key] = value_encoded
        self.trigger_changed(key)

        return self

    def __eq__(self, other):
        if not isinstance(other, DatastoreDict):
            return False

        keys = set(self.data.keys()) & set(other.data.keys())
        return (len(self) == len(other) == len(keys) and
                all(self.data[k] == other.data[k] for k in keys))

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return (k for k in self.data.keys())

    def __contains__(self, key):
        """Test whether key is set."""
        return key in self.data

    def __delitem__(self, key):
        """Delete the given key."""
        del self.data[key]
        self.trigger_changed(key)

    def keys(self):
        return self.data.keys()

    def values(self):
        return (self[k] for k in self.data.keys())

    def items(self):
        return ((k, self[k]) for k, v in self.data.keys())

    def update(self, new_data):
        for k, v in new_data.items():
            self[k] = v

        return self


class Datastore(object):
    """Key-value data store.

    An in-memory and in-process (not persistent) key-value store.

    :param domain:
        A namespace for the key values. This can be an analysis instance id for
        data local to an analysis instance or the name of an analysis class
        for data that is shared across instances of the same analysis.
    """
    store = defaultdict(DatastoreDict)
    change_callbacks = defaultdict(list)

    def __init__(self, domain):
        self.domain = domain
        datastore_dict = Datastore.store[self.domain]
        datastore_dict._change_callback = self.trigger_change_callbacks

    def on_change(self, callback):
        """Register a change callback.

        :param callback: Function that takes in a key and a value.
        """
        Datastore.change_callbacks[self.domain].append(callback)
        return self

    def trigger_change_callbacks(self, key):
        for callback in Datastore.change_callbacks[self.domain]:
            callback(key, Datastore.store[self.domain].get(key, None))

    def trigger_all_change_callbacks(self):
        """Trigger all callbacks that were set with on_change()."""
        for key in Datastore.store[self.domain].keys():
            self.trigger_change_callbacks(key)

    def __setitem__(self, key, value):
        """Set value for given key.

        Allows for assignments of the form ``d[key] = value``.
        Callbacks are skipped if the json-encoded value is unchanged.
        """
        Datastore.store[self.domain][key] = value
        return self

    def __getitem__(self, key):
        """Return the value for the given key."""
        return Datastore.store[self.domain][key]

    def __delitem__(self, key):
        """Delete the given key."""
        del Datastore.store[self.domain][key]
        self.trigger_change_callbacks(key)

    def __contains__(self, key):
        """Test whether key is set."""
        return key in Datastore.store[self.domain]

    def update(self, key_value_pairs):
        """Similar to ``dict.update()``.

        :param dict key_value_pairs:
            A dictionary of key value pairs to update.
        """
        Datastore.store[self.domain].update(key_value_pairs)

    def init(self, key_value_pairs):
        """Initialize datastore.

        Only sets values for keys that are not in the datastore already.

        :param dict key_value_pairs:
            A set of key value pairs to use to initialize the datastore.
        """
        for k, v in key_value_pairs.items():
            if k not in Datastore.store[self.domain]:
                Datastore.store[self.domain][k] = v
