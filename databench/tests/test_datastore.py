import databench
import unittest


class Datastore(unittest.TestCase):
    def setUp(self):
        self.n_callbacks = 0
        self.after = None
        self.d = databench.Datastore('abcdef')
        self.d.subscribe(self.datastore_callback)
        self.after = {}

    def tearDown(self):
        self.d.close()

    def datastore_callback(self, key_value):
        self.n_callbacks += 1
        print('changed to {}'.format(key_value))
        self.after.update(key_value)
        return 'callback return'

    def test_simple(self):
        self.d.set('test', 'trivial')
        self.assertEqual(self.after, {'test': 'trivial'})

    def test_init(self):
        self.d.set('test', 'before-init')
        self.d.init({'unset_test': 'init'})
        self.assertEqual(self.d['test'], 'before-init')
        self.assertEqual(self.d['unset_test'], 'init')

    def test_del_callback(self):
        self.n_callback2 = 0

        def callback2(key_value):
            self.n_callback2 += 1

        d2 = databench.Datastore('abcdef').subscribe(callback2)
        self.d.set('test', 'del-callback')
        d2.close()
        self.d.set('test', 'del-callback2')
        self.assertEqual(self.n_callback2, 1)

    def test_list(self):
        self.d.set('test', ['list'])
        self.assertEqual(self.after['test'], ['list'])

    def test_list_change(self):
        self.d.set('test', ['list'])
        self.d.set('test', ['list2'])
        self.assertEqual(self.after['test'], ['list2'])

    def test_list_change_element(self):
        self.d.set('test', ['list'])
        self.d.set('test', ['modified list'])
        self.assertEqual(self.after['test'], ['modified list'])

    def test_dict(self):
        self.d.set('test', {'key': 'value'})
        self.assertEqual(self.after, {'test': {'key': 'value'}})

    def test_dict_change(self):
        self.d.set('test', {'key': 'value'})
        self.d.set('test', {'key': 'value2'})
        self.assertEqual(self.after, {'test': {'key': 'value2'}})

    def test_dict_change_element(self):
        self.d.set('test', {'key': 'value'})
        self.d.set('test', {'key': 'modified value'})
        self.assertEqual(self.after, {'test': {'key': 'modified value'}})

    def test_dict_change_element2(self):
        self.d.set('test', {'key': 'value'})
        all = self.d['test']
        all['key'] = 'modified value'
        self.d.set('test', all)
        self.assertEqual(self.after, {'test': {'key': 'modified value'}})

    def test_dict_change_element3(self):
        self.d.set('test', {'key': {'key2': 'value'}})
        all = self.d['test']
        all['key']['key2'] = 'modified'
        self.d.set('test', all)
        self.assertEqual(self.after, {'test': {'key': {'key2': 'modified'}}})

    def test_dict_overwrite(self):
        self.d.set('test', {'key': 'value'})
        self.d.set('test', {'key': 'modified value'})
        self.assertEqual(self.after, {'test': {'key': 'modified value'}})

    def test_dict_overwrite2(self):
        self.d.set('test', {'e': 1})
        self.d.set('test', {'e': 1, 'h': 1})
        self.assertEqual(self.after, {'test': {'e': 1, 'h': 1}})

    def test_dict_update(self):
        self.d.set_state({'key': 'value'})
        self.d.set_state({'key': 'mod', 'key2': 'new'})
        self.assertEqual(self.after, {'key': 'mod', 'key2': 'new'})

    def test_cycle(self):
        self.d.set('test', {'key': 'value'})
        n_callbacks_before = self.n_callbacks
        test = self.d['test']
        test['key'] = 'modified'
        self.d.set('test', test)
        self.assertEqual(self.n_callbacks, n_callbacks_before + 1)
        self.assertEqual(self.after['test'], {'key': 'modified'})

    def test_cycle2(self):
        self.d.set('test', {'key': {'key2': 'value'}})
        n_callbacks_before = self.n_callbacks
        self.d.set('test', {'key': {'key2': 'modified'}})
        self.assertEqual(self.n_callbacks, n_callbacks_before + 1)
        self.assertEqual(self.after['test'], {'key': {'key2': 'modified'}})

    def test_contains(self):
        self.d.set('test', 'contains')
        assert 'test' in self.d
        assert 'never-used-test' not in self.d

    def test_set_return(self):
        ret = self.d.set('test', 'set_return')
        assert 'test' in self.d
        self.assertEqual(ret, ['callback return'])

    def test_setstate(self):
        self.d.set('test', 'setstate')
        self.d.set_state({'test': 'modified'})
        self.assertEqual(self.after['test'], 'modified')

    def test_setstate_fn(self):
        self.d.set('test', 'setstate')
        self.d.set('cnt', 2)
        self.d.set_state(lambda ds: {'test': 'modified{}'.format(ds['cnt'])})
        self.assertEqual(self.after['test'], 'modified2')


class DatastoreLegacy(unittest.TestCase):
    def setUp(self):
        self.n_callbacks = 0
        self.after = None
        self.d = databench.DatastoreLegacy('abcdef')
        self.d.on_change(self.datastore_callback)

    def tearDown(self):
        self.d.close()

    def datastore_callback(self, key, value):
        self.n_callbacks += 1
        print('{} changed to {}'.format(key, value))
        self.after = value
        return 'callback return'

    def test_simple(self):
        self.d['test'] = 'trivial'
        self.assertEqual(self.after, 'trivial')

    def test_init(self):
        self.d['test'] = 'before-init'
        self.d.init({'unset_test': 'init'})
        self.assertEqual(self.d['test'], 'before-init')
        self.assertEqual(self.d['unset_test'], 'init')

    def test_del_callback(self):
        self.n_callback2 = 0

        def callback2(key, value):
            self.n_callback2 += 1

        d2 = databench.DatastoreLegacy('abcdef').on_change(callback2)
        self.d['test'] = 'del-callback'
        d2.close()
        self.d['test'] = 'del-callback2'
        self.assertEqual(self.n_callback2, 1)

    def test_update(self):
        self.d.update({'test': 'update'})
        self.assertEqual(self.after, 'update')

    def test_delete(self):
        self.d.update({'test': 'delete'})
        self.assertEqual(self.after, 'delete')
        del self.d['test']
        self.assertNotIn('test', self.d)

    def test_list(self):
        self.d['test'] = ['list']
        self.assertEqual(list(self.after), ['list'])

    def test_list_change(self):
        self.d['test'] = ['list']
        self.d['test'] = ['list2']
        self.assertEqual(list(self.after), ['list2'])

    def test_list_change_element(self):
        self.d['test'] = ['list']
        self.d['test'][0] = 'modified list'
        self.assertEqual(list(self.after), ['modified list'])

    def test_dict(self):
        self.d['test'] = {'key': 'value'}
        self.assertEqual(self.after.to_native(), {'key': 'value'})

    def test_dict_change(self):
        self.d['test'] = {'key': 'value'}
        self.d['test'] = {'key': 'value2'}
        self.assertEqual(self.after.to_native(), {'key': 'value2'})

    def test_dict_change_element(self):
        self.d['test'] = {'key': 'value'}
        self.d['test']['key'] = 'modified value'
        self.assertEqual(self.after.to_native(), {'key': 'modified value'})

    def test_dict_change_element2(self):
        self.d['test'] = {'key': 'value'}
        all = self.d['test']
        all['key'] = 'modified value'
        self.d['test'] = all
        self.assertEqual(self.after.to_native(), {'key': 'modified value'})

    def test_dict_change_element3(self):
        self.d['test'] = {'key': {'key2': 'value'}}
        all = self.d['test']
        all['key']['key2'] = 'modified'
        self.d['test'] = all
        self.assertEqual(self.after.to_native(), {'key': {'key2': 'modified'}})

    def test_dict_overwrite(self):
        self.d['test'] = {'key': 'value'}
        self.d['test'] = {'key': 'modified value'}
        self.assertEqual(self.after.to_native(), {'key': 'modified value'})

    def test_dict_overwrite2(self):
        self.d['test'] = {'e': 1}
        self.d['test'] = {'e': 1, 'h': 1}
        self.assertEqual(self.after.to_native(), {'e': 1, 'h': 1})

    def test_dict_update(self):
        self.d['test'] = {'key': 'value'}
        self.d['test'].update({'key': 'mod', 'key2': 'new'})
        self.assertEqual(self.after.to_native(), {'key': 'mod', 'key2': 'new'})

    def test_cycle(self):
        self.d['test'] = {'key': 'value'}
        n_callbacks_before = self.n_callbacks
        test = self.d['test']
        test['key'] = 'modified'
        self.d['test'] = test
        self.assertEqual(self.n_callbacks, n_callbacks_before + 1)
        self.assertEqual(self.after.to_native(), {'key': 'modified'})

    def test_cycle2(self):
        self.d['test'] = {'key': {'key2': 'value'}}
        n_callbacks_before = self.n_callbacks
        self.d['test']['key']['key2'] = 'modified'
        self.assertEqual(self.n_callbacks, n_callbacks_before + 1)
        self.assertEqual(self.after.to_native(), {'key': {'key2': 'modified'}})

    def test_contains(self):
        self.d['test'] = 'contains'
        assert 'test' in self.d
        assert 'never-used-test' not in self.d

    def test_set_return(self):
        ret = self.d.set('test', 'set_return')
        assert 'test' in self.d
        self.assertEqual(ret, ['callback return'])

    def test_analysis_datastore(self):
        a = databench.Analysis().init_databench()
        a.set_emit_fn(lambda s, pl: None)
        a.data.on_change(self.datastore_callback)
        a.data['test'] = 'analysis_datastore'

        print(self.after)
        self.assertEqual(self.after, 'analysis_datastore')


if __name__ == '__main__':
    unittest.main()
