"""Simple test."""

import databench
import ssl
import tornado.testing


class App(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return databench.App().tornado_app()

    def test_index(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)


class SSLApp(tornado.testing.AsyncHTTPSTestCase):
    def get_app(self):
        return databench.App().tornado_app()

    def test_index(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)

    def test_certificate(self):
        """expect self-signed certificate to fail validation"""
        response = self.fetch("/", validate_cert=True)
        self.assertEqual(response.code, 599)
        self.assertIsInstance(response.error, ssl.SSLError)
