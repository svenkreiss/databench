from collections import defaultdict
import copy
import logging

log = logging.getLogger(__name__)


class Datastore(object):
    store = defaultdict(dict)
    on_change_cb = defaultdict(list)

    def __init__(self, domain):
        self.domain = domain

    def on_change(self, cb):
        Datastore.on_change_cb[self.domain].append(cb)
        return self

    def __setitem__(self, key, value):
        if key in Datastore.store[self.domain] and \
           Datastore.store[self.domain][key] == value:
            return self

        value = copy.deepcopy(value)

        Datastore.store[self.domain][key] = value
        for cb in Datastore.on_change_cb[self.domain]:
            cb(key, value)

        return self

    def __getitem__(self, key):
        return Datastore.store[self.domain][key]

    def __contains__(self, key):
        return key in Datastore.store[self.domain]

    def update(self, d):
        """Similar to dict.update(). Call callbacks on each changed key."""
        for k, v in d.items():
            self[k] = v

    def init(self, d):
        """Only sets values that are not set already.

        No callbacks are called.
        """
        for k, v in d.items():
            if k not in Datastore.store[self.domain]:
                Datastore.store[self.domain][k] = copy.deepcopy(v)
