"""Simple test."""

import databench
import ssl


class App(databench.testing.ConnectionTestCase):
    def test_index(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)

    def test_dummypi(self):
        response = self.fetch('/dummypi/')
        self.assertEqual(response.code, 200)


class SSLApp(databench.testing.ConnectionTestCaseSSL):
    def test_index(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)

    def test_certificate(self):
        """expect self-signed certificate to fail validation"""
        response = self.fetch("/", validate_cert=True)
        self.assertEqual(response.code, 599)
        self.assertIsInstance(response.error, ssl.SSLError)
