from collections import defaultdict


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

        Datastore.store[self.domain][key] = value
        for cb in Datastore.on_change_cb[self.domain]:
            cb(key, value)

        return self

    def __getitem__(self, key):
        return Datastore.store[self.domain][key]

    def update(self, d):
        for k, v in d.items():
            self[k] = v
