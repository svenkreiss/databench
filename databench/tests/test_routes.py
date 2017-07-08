from databench.testing import ConnectionTestCase

try:
    from urllib import urlencode  # Python 2
except ImportError:
    from urllib.parse import urlencode  # Python 3


class RoutesTest(ConnectionTestCase):
    analyses_path = 'databench.tests.analyses'

    def test_get(self):
        response = self.fetch('/simple2/get')
        self.assertEqual(response.code, 200)

    def test_post(self):
        body = urlencode({'data': 'test data'})
        response = self.fetch('/simple2/post', method='POST', body=body)
        self.assertEqual(response.code, 200)
