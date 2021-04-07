# standard library
import unittest
import base64

from json import loads
from flask.testing import FlaskClient
from flask import Response
from delphi.epidata.server.main import app

# py3tester coverage target
__test_target__ = "delphi.epidata.server.endpoints.covidcast"


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    client: FlaskClient

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        self.client = app.test_client()

    def test_url(self):
        rv: Response = self.client.get('/covidcast/', follow_redirects=True)
        msg = rv.get_json()
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(msg['result'], -1)
        self.assertRegex(msg['message'], r"missing parameter.*")

    def test_time(self):
        rv: Response = self.client.get('/covidcast/', query_string=dict(signal="src1:*", time="day:20200101", geo="state:*"))
        msg = rv.get_json()
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(msg['result'], -2)  # no result
        self.assertEqual(msg['message'], "no results")
