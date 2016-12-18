import databench
import unittest


class TestDatastore(unittest.TestCase):
    def setUp(self):
        self.data_after = None
        self.d = databench.Datastore('abcdef').on_change(self.cb)

    def cb(self, key, value):
        print('{} changed to {}'.format(key, value))
        self.data_after = value

    def test_simple(self):
        self.d['test'] = 'trivial'
        self.assertEqual(self.data_after, 'trivial')

    def test_init(self):
        self.d['test'] = 'before-init'
        self.d.init({'unset_test': 'init'})
        self.assertEqual(self.data_after, 'before-init')

    def test_update(self):
        self.d.update({'test': 'update'})
        self.assertEqual(self.data_after, 'update')

    def test_delete(self):
        self.d.update({'test': 'delete'})
        self.assertEqual(self.data_after, 'delete')
        del self.d['test']
        self.assertNotIn('test', self.d)

    def test_list(self):
        self.d['test'] = ['list']
        self.assertEqual(list(self.data_after), ['list'])

    def test_list_change_element(self):
        self.d['test'] = ['list']
        self.d['test'][0] = 'modified list'
        self.assertEqual(list(self.data_after), ['modified list'])

    def test_dict(self):
        self.d['test'] = {'key': 'value'}
        self.assertEqual(dict(self.data_after), {'key': 'value'})

    def test_dict_change_element(self):
        self.d['test'] = {'key': 'value'}
        self.d['test']['key'] = 'modified value'
        self.assertEqual(dict(self.data_after), {'key': 'modified value'})

    def test_dict_overwrite(self):
        self.d['test'] = {'key': 'value'}
        self.d['test'] = {'key': 'modified value'}
        self.assertEqual(dict(self.data_after), {'key': 'modified value'})

    def test_dict_overwrite2(self):
        self.d['test'] = {'e': 1}
        self.d['test'] = {'e': 1, 'h': 1}
        self.assertEqual(dict(self.data_after), {'e': 1, 'h': 1})

    def test_dict_update(self):
        self.d['test'] = {'key': 'value'}
        self.d['test'].update({'key': 'mod', 'key2': 'new'})
        self.assertEqual(dict(self.data_after), {'key': 'mod', 'key2': 'new'})

    def test_contains(self):
        self.d['test'] = 'contains'
        assert 'test' in self.d
        assert 'never-user-test' not in self.d

    def test_analysis_datastore(self):
        a = databench.Analysis()
        a.set_emit_fn(lambda s, pl: None)
        a.data.on_change(self.cb)
        a.data['test'] = 'analysis_datastore'

        print(self.data_after)
        self.assertEqual(self.data_after, 'analysis_datastore')


if __name__ == '__main__':
    unittest.main()
