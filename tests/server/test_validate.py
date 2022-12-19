"""Unit tests for granular sensor authentication in api.php."""

# standard library
import unittest
import base64

# from flask.testing import FlaskClient
from delphi.epidata.server._common import app
from delphi.epidata.server._validate import (
    resolve_auth_token,
    check_auth_token,
    require_all,
    require_any,
)
from delphi.epidata.server._exceptions import (
    ValidationFailedException,
    UnAuthenticatedException,
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

    def test_resolve_auth_token(self):
        with self.subTest("no auth"):
            with app.test_request_context("/"):
                self.assertIsNone(resolve_auth_token())

        with self.subTest("param"):
            with app.test_request_context("/?auth=abc"):
                self.assertEqual(resolve_auth_token(), "abc")

        with self.subTest("bearer token"):
            with app.test_request_context("/", headers={"Authorization": "Bearer abc"}):
                self.assertEqual(resolve_auth_token(), "abc")

        with self.subTest("basic token"):
            userpass = base64.b64encode(b"epidata:abc").decode("utf-8")
            with app.test_request_context(
                "/", headers={"Authorization": f"Basic {userpass}"}
            ):
                self.assertEqual(resolve_auth_token(), "abc")

    def test_check_auth_token(self):
        with self.subTest("no auth but optional"):
            with app.test_request_context("/"):
                self.assertFalse(check_auth_token("abc", True))
        with self.subTest("no auth but required"):
            with app.test_request_context("/"):
                self.assertRaises(
                    ValidationFailedException, lambda: check_auth_token("abc")
                )
        with self.subTest("auth and required"):
            with app.test_request_context("/?auth=abc"):
                self.assertTrue(check_auth_token("abc"))
        with self.subTest("auth and required but wrong"):
            with app.test_request_context("/?auth=abc"):
                self.assertRaises(
                    UnAuthenticatedException, lambda: check_auth_token("def")
                )
        with self.subTest("auth and required but wrong but optional"):
            with app.test_request_context("/?auth=abc"):
                self.assertFalse(check_auth_token("def", True))

    def test_require_all(self):
        with self.subTest("all given"):
            with app.test_request_context("/"):
                self.assertTrue(require_all())
            with app.test_request_context("/?abc=abc&def=3"):
                self.assertTrue(require_all("abc", "def"))
        with self.subTest("missing parameter"):
            with app.test_request_context("/?abc=abc"):
                self.assertRaises(
                    ValidationFailedException, lambda: require_all("abc", "def")
                )
        with self.subTest("missing empty parameter"):
            with app.test_request_context("/?abc=abc&def="):
                self.assertRaises(
                    ValidationFailedException, lambda: require_all("abc", "def")
                )

    def test_require_any(self):
        with self.subTest("default given"):
            with app.test_request_context("/"):
                self.assertRaises(ValidationFailedException, lambda: require_any("abc"))
        with self.subTest("one option give"):
            with app.test_request_context("/?abc=abc"):
                self.assertTrue(require_any("abc", "def"))
        with self.subTest("multiple options given"):
            with app.test_request_context("/?abc=abc&def=d"):
                self.assertTrue(require_any("abc", "def"))
        with self.subTest("one options given with is empty"):
            with app.test_request_context("/?abc="):
                self.assertRaises(ValidationFailedException, lambda: require_any("abc"))
        with self.subTest("one options given with is empty but ok"):
            with app.test_request_context("/?abc="):
                self.assertTrue(require_any("abc", empty=True))
