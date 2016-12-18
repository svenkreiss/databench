from .utils import json_encoder_default
from collections import defaultdict
from future.builtins import zip
import json
import logging

log = logging.getLogger(__name__)


class DatastoreList(object):
    """Object wrapper for storing a list in Datastore.

    This triggers callbacks when elements are modified.
    """
    def __init__(self, data, callback):
        self.data = [json.dumps(v, default=json_encoder_default) for v in data]
        self.callback = callback

    def __getitem__(self, key):
        return json.loads(self.data[key])

    def __setitem__(self, key, value):
        value_encoded = json.dumps(value, default=json_encoder_default)

        if key in self.data and self.data[key] == value_encoded:
            return self

        self.data[key] = value_encoded
        self.callback(self)

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

    This triggers callbacks when elements are modified.
    """
    def __init__(self, data, callback):
        self.data = {k: json.dumps(v, default=json_encoder_default)
                     for k, v in data.items()}
        self.callback = callback

    def __getitem__(self, key):
        if key not in self.data:
            raise IndexError
        return json.loads(self.data[key])

    def __setitem__(self, key, value):
        value_encoded = json.dumps(value, default=json_encoder_default)

        if key in self.data and self.data[key] == value_encoded:
            return self

        self.data[key] = value_encoded
        self.callback(self)

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

    def keys(self):
        return self.data.keys()

    def values(self):
        return (json.loads(v) for v in self.data.values())

    def items(self):
        return ((k, json.loads(v)) for k, v in self.data.items())

    def update(self, new_data):
        new_data_encoded = {k: json.dumps(v, default=json_encoder_default)
                            for k, v in new_data.items()}
        self.data.update(new_data_encoded)
        self.callback(self)

        return self


class Datastore(object):
    """Key-value data store.

    An in-memory and in-process (not persistent) key-value store.

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
        """Register a change callback.

        :param callback:
            A callback function that takes in a key and a value.
        """
        Datastore.on_change_cb[self.domain].append(callback)
        return self

    def __setitem__(self, key, value):
        """Set value for given key.

        Allows for assignments of the form ``d[key] = value``. The value is
        encoded as json before it is stored.

        Callbacks are skipped if the json-encoded value is unchanged.
        """
        cb_fn = self.callback_fn(key)
        if isinstance(value, list):
            value_encoded = DatastoreList(value, cb_fn)
        elif isinstance(value, dict):
            value_encoded = DatastoreDict(value, cb_fn)
        else:
            value_encoded = json.dumps(value, default=json_encoder_default)

        if key in Datastore.store[self.domain] and \
           Datastore.store[self.domain][key] == value_encoded:
            return self

        Datastore.store[self.domain][key] = value_encoded

        value_decoded = self.decode(value_encoded)
        cb_fn(value_decoded)

        return self

    def callback_fn(self, key):
        def execute(value):
            for cb in Datastore.on_change_cb[self.domain]:
                cb(key, value)
        return execute

    def decode(self, value):
        if isinstance(value, DatastoreList):
            return value
        elif isinstance(value, DatastoreDict):
            return value

        return json.loads(value)

    def __getitem__(self, key):
        """Return the value for the given key."""
        return self.decode(Datastore.store[self.domain][key])

    def get_encoded(self, key):
        """Return the stored value without decoding it."""
        return Datastore.store[self.domain][key]

    def __delitem__(self, key):
        """Delete the given key."""
        del Datastore.store[self.domain][key]
        for cb in Datastore.on_change_cb[self.domain]:
            cb(key, None)

    def __contains__(self, key):
        """Test whether key is set."""
        return key in Datastore.store[self.domain]

    def update(self, key_value_pairs):
        """Similar to ``dict.update()``.

        :param dict key_value_pairs:
            A dictionary of key value pairs to update.
        """
        for k, v in key_value_pairs.items():
            self[k] = v

    def init(self, key_value_pairs):
        """Initialize datastore.

        Only sets values for keys that are not in the datastore already.
        No callbacks are called.

        :param dict key_value_pairs:
            A set of key value pairs to use to initialize the datastore.
        """
        for k, v in key_value_pairs.items():
            if k not in Datastore.store[self.domain]:
                Datastore.store[self.domain][k] = v
