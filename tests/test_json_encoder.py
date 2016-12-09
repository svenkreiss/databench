from databench.utils import json_encoder_default
import json
import unittest


class TestJsonEncoder(unittest.TestCase):
    def test_nan(self):
        data = json.dumps(float('NaN'), default=json_encoder_default)
        self.assertEqual(data, 'NaN')

    def test_inf(self):
        data = json.dumps(float('inf'), default=json_encoder_default)
        self.assertEqual(data, 'Infinity')

    def test_neg_inf(self):
        data = json.dumps(float('-inf'), default=json_encoder_default)
        self.assertEqual(data, '-Infinity')

    def test_list(self):
        data = json.dumps([1, float('inf')], default=json_encoder_default)
        self.assertEqual(data, '[1, Infinity]')

    def test_dict(self):
        data = json.loads(json.dumps({'one': 1, 'inf': float('inf')},
                                     default=json_encoder_default))
        self.assertEqual(data, {'one': 1, 'inf': float('inf')})

    def test_set(self):
        data = json.dumps({1, float('inf')}, default=json_encoder_default)
        self.assertEqual(data, '[1, Infinity]')

    def test_tuple(self):
        data = json.dumps((1, float('inf')), default=json_encoder_default)
        self.assertEqual(data, '[1, Infinity]')


if __name__ == '__main__':
    unittest.main()
