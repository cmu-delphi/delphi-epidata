# standard library
import unittest

from flask import request

# from flask.testing import FlaskClient
from delphi.epidata.server._common import app
from delphi.epidata.server._validate import (
    require_all,
    require_any,
)
from delphi.epidata.server._exceptions import (
    ValidationFailedException,
)

# py3tester coverage target
__test_target__ = "delphi.epidata.server._validate"


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    # app: FlaskClient

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        self.client = app.test_client()

    def test_require_all(self):
        with self.subTest("all given"):
            with app.test_request_context("/"):
                self.assertTrue(require_all(request))
            with app.test_request_context("/?abc=abc&def=3"):
                self.assertTrue(require_all(request, "abc", "def"))
        with self.subTest("missing parameter"):
            with app.test_request_context("/?abc=abc"):
                self.assertRaises(
                    ValidationFailedException, lambda: require_all(request, "abc", "def")
                )
        with self.subTest("missing empty parameter"):
            with app.test_request_context("/?abc=abc&def="):
                self.assertRaises(
                    ValidationFailedException, lambda: require_all(request, "abc", "def")
                )

    def test_require_any(self):
        with self.subTest("default given"):
            with app.test_request_context("/"):
                self.assertRaises(ValidationFailedException, lambda: require_any(request, "abc"))
        with self.subTest("one option give"):
            with app.test_request_context("/?abc=abc"):
                self.assertTrue(require_any(request, "abc", "def"))
        with self.subTest("multiple options given"):
            with app.test_request_context("/?abc=abc&def=d"):
                self.assertTrue(require_any(request, "abc", "def"))
        with self.subTest("one options given with is empty"):
            with app.test_request_context("/?abc="):
                self.assertRaises(ValidationFailedException, lambda: require_any(request, "abc"))
        with self.subTest("one options given with is empty but ok"):
            with app.test_request_context("/?abc="):
                self.assertTrue(require_any(request, "abc", empty=True))

    def test_origin_headers(self):
        with self.subTest("referer only"):
            with self.assertLogs("server_api", level='INFO') as logs:
                self.client.get("/signal_dashboard_status", headers={
                    "Referer": "https://test.com/test"
                })
            output = logs.output
            self.assertEqual(len(output), 2) # [before_request, after_request]
            self.assertIn("Received API request", output[0])
            self.assertIn("\"referrer\": \"https://test.com/test\"", output[0])
            self.assertIn("Served API request", output[1])
            self.assertIn("\"referrer\": \"https://test.com/test\"", output[1])
        with self.subTest("origin only"):
            with self.assertLogs("server_api", level='INFO') as logs:
                self.client.get("/signal_dashboard_status", headers={
                    "Origin": "https://test.com"
                })
            output = logs.output
            self.assertEqual(len(output), 2) # [before_request, after_request]
            self.assertIn("Received API request", output[0])
            self.assertIn("\"referrer\": \"https://test.com\"", output[0])
            self.assertIn("Served API request", output[1])
            self.assertIn("\"referrer\": \"https://test.com\"", output[1])
        with self.subTest("referer overrides origin"):
            with self.assertLogs("server_api", level='INFO') as logs:
                self.client.get("/signal_dashboard_status", headers={
                    "Referer": "https://test.com/test",
                    "Origin": "https://test.com"
                })
            output = logs.output
            self.assertEqual(len(output), 2) # [before_request, after_request]
            self.assertIn("Received API request", output[0])
            self.assertIn("\"referrer\": \"https://test.com/test\"", output[0])
            self.assertIn("Served API request", output[1])
            self.assertIn("\"referrer\": \"https://test.com/test\"", output[1])
