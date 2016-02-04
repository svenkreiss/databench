import databench

data_after = None


def test_datastore():
    def cb(key, value):
        global data_after
        print('{} changed to {}'.format(key, value))
        data_after = value

    d = databench.Datastore('abcdef').add_change_cb(cb)
    d['test'] = 'trivial'

    assert data_after == 'trivial'


def test_analysis_datastore():
    def cb(key, value):
        global data_after
        print('{} changed to {}'.format(key, value))
        data_after = value

    a = databench.Analysis().add_data_change_cb(cb)
    a.data['test'] = 'analysis_datastore'

    print(data_after)
    assert data_after == 'analysis_datastore'


if __name__ == '__main__':
    test_datastore()
    test_analysis_datastore()
