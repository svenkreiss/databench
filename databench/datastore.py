from .utils import json_encoder_default
from collections import defaultdict
import json
import logging

log = logging.getLogger(__name__)


class DatastoreList(object):
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
        return (len(self) == len(other) and
                all(v1 == v2 for v1, v2 in zip(self.data, other.data)))

    def __len__(self):
        return len(self.data)


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
