"""Unit tests for granular sensor authentication in api.php."""

# standard library
import unittest
import base64

# from flask.testing import FlaskClient
from delphi.epidata.server._common import app
from delphi.epidata.server._security import (
    resolve_auth_token,
)

# py3tester coverage target
__test_target__ = "delphi.epidata.server._security"


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    # app: FlaskClient

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False

    def test_resolve_auth_token(self):
        with self.subTest("no auth"):
            with app.test_request_context("/"):
                self.assertIsNone(resolve_auth_token())

        with self.subTest("param"):
            with app.test_request_context("/?auth=abc"):
                self.assertEqual(resolve_auth_token(), "abc")

        with self.subTest("param2"):
            with app.test_request_context("/?api_key=abc"):
                self.assertEqual(resolve_auth_token(), "abc")

        with self.subTest("bearer token"):
            with app.test_request_context("/", headers={"Authorization": "Bearer abc"}):
                self.assertEqual(resolve_auth_token(), "abc")

        with self.subTest("basic token"):
            userpass = base64.b64encode(b"epidata:abc").decode("utf-8")
            with app.test_request_context("/", headers={"Authorization": f"Basic {userpass}"}):
                self.assertEqual(resolve_auth_token(), "abc")
