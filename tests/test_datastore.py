import databench


data_after = None


def cb(key, value):
    global data_after
    print('{} changed to {}'.format(key, value))
    data_after = value


d = databench.Datastore('abcdef').on_change(cb)


def test_datastore():
    d['test'] = 'trivial'
    assert data_after == 'trivial'


def test_datastore_list():
    d['test'] = ['list']
    assert data_after == ['list']


def test_datastore_dict():
    d['test'] = {'key': 'value'}
    assert data_after == {'key': 'value'}


def test_analysis_datastore():
    a = databench.Analysis()
    a.set_emit_fn(lambda s, pl: None)
    a.data.on_change(cb)
    a.data['test'] = 'analysis_datastore'

    print(data_after)
    assert data_after == 'analysis_datastore'


if __name__ == '__main__':
    test_datastore()
    test_datastore_list()
    test_datastore_dict()
    test_analysis_datastore()
