"""Regression tests for issue #1809.

1. With ``Epidata.sandbox = True`` the client must return the standard
   ``{result, message, epidata}`` envelope so the documented
   ``Epidata.check(...)`` error-handling pattern works offline. (Before the
   fix, ``_request`` returned Python ``True`` and ``check`` raised
   ``TypeError: 'bool' object is not subscriptable``.)
2. ``_request_with_retry`` / ``_request`` must not use a mutable ``{}``
   default for ``params`` (latent shared-state hazard).
"""

# standard library
import inspect
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "client"))

import delphi_epidata  # noqa: E402  (import-time _version_check() phones home; failures are logged, not raised)
from delphi_epidata import Epidata  # noqa: E402


class SandboxEnvelopeTests(unittest.TestCase):
    """Sandbox mode must return a well-formed envelope, not a bare ``True``."""

    def setUp(self):
        Epidata.sandbox = True

    def tearDown(self):
        Epidata.sandbox = False

    def test_sandbox_returns_envelope_dict(self):
        resp = Epidata._request("fluview", {"regions": "nat", "epiweeks": 202001})
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp["result"], 1)
        self.assertIn("message", resp)
        self.assertIn("epidata", resp)

    def test_sandbox_works_with_check(self):
        # the documented error-handling pattern must work in sandbox mode
        resp = Epidata._request("fluview", {"regions": "nat", "epiweeks": 202001})
        self.assertEqual(Epidata.check(resp), [])

    def test_sandbox_no_params_arg(self):
        # endpoints called without params must also get the envelope
        resp = Epidata._request("fluview_meta")
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp["result"], 1)


class NoMutableDefaultsTests(unittest.TestCase):
    """``params`` must default to ``None``, not a shared ``{}``."""

    def test_no_mutable_default_params(self):
        for fn in (Epidata._request_with_retry, Epidata._request):
            default = inspect.signature(fn).parameters["params"].default
            self.assertIsNone(
                default,
                f"{fn.__name__} uses a mutable default for params",
            )


if __name__ == "__main__":
    unittest.main()
