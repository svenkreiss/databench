"""Simple test."""

import databench
import tornado.testing
import unittest


class App(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return databench.App().tornado_app()

    def test_index(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)


if __name__ == '__main__':
    unittest.main()
