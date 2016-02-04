from collections import defaultdict


class Datastore(object):
    store = defaultdict(dict)
    on_change_cb = defaultdict(list)

    def __init__(self, domain):
        self.domain = domain

    def add_change_cb(self, cb):
        Datastore.on_change_cb[self.domain].append(cb)
        return self

    def __setitem__(self, key, value):
        Datastore.store[self.domain][key] = value
        for cb in Datastore.on_change_cb[self.domain]:
            cb(key, value)
        return self

    def __getitem__(self, key):
        return Datastore.store[self.domain][key]
