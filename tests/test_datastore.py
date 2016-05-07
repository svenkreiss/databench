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


def test_init():
    d['test'] = 'before-init'
    d.init({'unset_test': 'init'})
    assert data_after == 'before-init'


def test_update():
    d.update({'test': 'update'})
    assert data_after == 'update'


def test_set_skip_callback():
    global data_after
    d['test'] = 'before-set'
    data_after = 'skip-callback'
    d['test'] = 'before-set'
    assert data_after == 'skip-callback'


def test_list():
    d['test'] = ['list']
    assert data_after == ['list']


def test_dict():
    d['test'] = {'key': 'value'}
    assert data_after == {'key': 'value'}


def test_contains():
    d['test'] = 'contains'
    assert 'test' in d
    assert 'never-user-test' not in d


def test_analysis_datastore():
    a = databench.Analysis()
    a.set_emit_fn(lambda s, pl: None)
    a.data.on_change(cb)
    a.data['test'] = 'analysis_datastore'

    print(data_after)
    assert data_after == 'analysis_datastore'


if __name__ == '__main__':
    test_datastore()
    test_init()
    test_update()
    test_list()
    test_dict()
    test_contains()
    test_analysis_datastore()
