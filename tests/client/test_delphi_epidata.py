"""Unit tests for delphi_epidata.py."""

# standard library
import importlib.util
import io
import os
import sys
import unittest

# third party
import requests

# py3tester coverage target
__test_target__ = "delphi.epidata.client.delphi_epidata"

try:
    from delphi.epidata.client import delphi_epidata as _client_module
except ImportError:  # pragma: no cover - fallback when the dev package is not installed
    _here = os.path.dirname(os.path.abspath(__file__))
    _module_path = os.path.normpath(
        os.path.join(_here, "..", "..", "src", "client", "delphi_epidata.py")
    )
    _spec = importlib.util.spec_from_file_location("delphi_epidata", _module_path)
    _client_module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_client_module)

Epidata = _client_module.Epidata
_redact_auth = getattr(_client_module, "_redact_auth", None)
_redact_params = getattr(_client_module, "_redact_params", None)
_helpers_available = _redact_auth is not None and _redact_params is not None


class _StubResponse:
    """Minimal stand-in for requests.Response."""

    def __init__(self, status_code=200):
        self.status_code = status_code
        self.content = b'{"result": 1}'

    def raise_for_status(self):
        pass


class DebugCredentialRedactionTests(unittest.TestCase):
    """Debug logging must never emit credentials to stderr (issue #1804)."""

    SECRET_AUTH = "SECRET-TOKEN-DO-NOT-LOG"
    SECRET_PARAM = "PARAM-SECRET-DO-NOT-LOG"

    def setUp(self):
        self._old_debug = Epidata.debug
        self._old_auth = Epidata.auth
        self._old_stderr = sys.stderr
        self._old_get = requests.get
        self._old_post = requests.post
        self.captured = io.StringIO()
        sys.stderr = self.captured
        Epidata.debug = True
        Epidata.auth = self.SECRET_AUTH
        self.request_kwargs = {}

    def tearDown(self):
        Epidata.debug = self._old_debug
        Epidata.auth = self._old_auth
        sys.stderr = self._old_stderr
        requests.get = self._old_get
        requests.post = self._old_post

    def _stub_get_200(self, url, params=None, **kwargs):
        self.request_kwargs["get"] = {"params": params, "kwargs": kwargs}
        return _StubResponse(200)

    def _stub_get_414_then_post_200(self, url, params=None, **kwargs):
        self.request_kwargs["get"] = {"params": params, "kwargs": kwargs}
        return _StubResponse(414)

    def _stub_post_200(self, url, params=None, **kwargs):
        self.request_kwargs["post"] = {"params": params, "kwargs": kwargs}
        return _StubResponse(200)

    def test_auth_kwarg_and_auth_param_redacted_in_debug_log(self):
        """The `auth` kwarg and any `auth` request param must be redacted."""
        requests.get = self._stub_get_200
        params = {"regions": "nat", "auth": self.SECRET_PARAM}
        Epidata._request_with_retry("fluview", params)

        logged = self.captured.getvalue()
        self.assertIn("Sending GET request", logged)
        self.assertNotIn(self.SECRET_AUTH, logged)
        self.assertNotIn(self.SECRET_PARAM, logged)
        self.assertIn("<redacted>", logged)

    def test_credentials_still_sent_on_the_wire(self):
        """Redaction is log-only: the real credentials must reach requests."""
        requests.get = self._stub_get_200
        params = {"regions": "nat", "auth": self.SECRET_PARAM}
        Epidata._request_with_retry("fluview", params)

        sent = self.request_kwargs["get"]
        self.assertEqual(sent["kwargs"]["auth"], self.SECRET_AUTH)
        self.assertEqual(sent["params"]["auth"], self.SECRET_PARAM)

    def test_414_retry_path_redacts_params(self):
        """The 414-retry POST debug log must not leak the `auth` param."""
        requests.get = self._stub_get_414_then_post_200
        requests.post = self._stub_post_200
        params = {"regions": "nat", "auth": self.SECRET_PARAM}
        Epidata._request_with_retry("fluview", params)

        logged = self.captured.getvalue()
        self.assertIn("retrying as POST", logged)
        self.assertNotIn(self.SECRET_PARAM, logged)
        self.assertNotIn(self.SECRET_AUTH, logged)

    @unittest.skipUnless(_helpers_available, "credential-redaction helpers not implemented")
    def test_redact_params_keeps_non_credentials_and_copies(self):
        """_redact_params redacts credential keys without mutating the input."""
        params = {"regions": "nat", "auth": "abc", "api_key": "xyz"}
        redacted = _redact_params(params)

        self.assertEqual(redacted["regions"], "nat")
        self.assertEqual(redacted["auth"], "<redacted>")
        self.assertEqual(redacted["api_key"], "<redacted>")
        # the caller's dict is untouched
        self.assertEqual(params["auth"], "abc")
        self.assertIsNot(redacted, params)

    @unittest.skipUnless(_helpers_available, "credential-redaction helpers not implemented")
    def test_redact_auth(self):
        """_redact_auth hides a set credential but preserves the unset state."""
        self.assertEqual(_redact_auth("token"), "<redacted>")
        self.assertEqual(_redact_auth(("user", "pass")), "<redacted>")
        self.assertIsNone(_redact_auth(None))


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    # TODO: Unit tests still need to be written. This no-op test will pass unless
    # the target file can't be loaded. In effect, it's a syntax checker.
    def test_syntax(self):
        pass
