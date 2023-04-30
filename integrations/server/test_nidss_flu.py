"""Unit tests for granular sensor authentication in api.php."""

import unittest

from delphi.epidata.server.main import app
from flask import Response
from flask.testing import FlaskClient

# py3tester coverage target
__test_target__ = "delphi.epidata.server.endpoints.nidss_flu"


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    client: FlaskClient

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        self.client = app.test_client()

    def test_urls(self):
        with self.subTest('direct url'):
            rv: Response = self.client.get('/nidss_flu', follow_redirects=True)
            msg = rv.get_json()
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(msg['result'], -1)
            self.assertRegex(msg['message'], r"missing parameter.*")
        with self.subTest('with wrapper'):
            rv: Response = self.client.get('/api.php?endpoint=nidss_flu', follow_redirects=True)
            msg = rv.get_json()
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(msg['result'], -1)
            self.assertRegex(msg['message'], r"missing parameter.*")

    def test_(self):
        rv: Response = self.client.get('/nidss_flu/', query_string=dict(regions="A", epiweeks="12"))
        msg = rv.get_json()
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(msg['result'], -2)  # no result
        self.assertEqual(msg['message'], "no results")
