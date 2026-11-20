"""Unit tests for client IP resolution behind reverse proxies (delphi-epidata#1802).

The anonymous rate-limit key is the client IP resolved by ``get_real_ip_addr``.
These tests pin the fail-closed behavior: only the rightmost ``depth`` entries
of the ``X-Forwarded-For`` chain were appended by trusted proxies, so a chain
shorter than the declared depth (over-declared depth, or a client connecting
directly) must fall back to the actual connecting peer instead of trusting
client-controlled entries.
"""

# standard library
import unittest
from unittest.mock import patch

from delphi.epidata.server._common import _resolve_client_ip, get_real_ip_addr

# py3tester coverage target
__test_target__ = "delphi.epidata.server._common"


class FakeRequest:
    """Minimal stand-in for a Flask request object."""

    def __init__(self, remote_addr, headers=None):
        self.remote_addr = remote_addr
        self.headers = headers or {}


class ResolveClientIpTests(unittest.TestCase):
    """Tests for the pure ``_resolve_client_ip`` helper."""

    def test_no_proxies_ignores_headers(self):
        self.assertEqual(
            _resolve_client_ip("10.0.0.9", "6.6.6.6", "7.7.7.7", 0), "10.0.0.9"
        )

    def test_no_headers_returns_remote_addr(self):
        self.assertEqual(_resolve_client_ip("10.0.0.9", None, None, 2), "10.0.0.9")

    def test_exact_depth_uses_leftmost_trusted_entry(self):
        # One trusted proxy appended "9.9.9.9"; the client-supplied "6.6.6.6" is stripped.
        self.assertEqual(
            _resolve_client_ip("10.0.0.9", "6.6.6.6, 9.9.9.9", None, 1), "9.9.9.9"
        )

    def test_chain_shorter_than_depth_falls_back_to_remote_addr(self):
        # The fix: a chain shorter than the declared depth contains no fully
        # trusted entry. Previously `chain[-depth:]` returned the whole chain
        # and the leftmost (client-controlled) entry was trusted.
        self.assertEqual(
            _resolve_client_ip("10.0.0.9", "6.6.6.6, 9.9.9.9", None, 4), "10.0.0.9"
        )
        self.assertEqual(_resolve_client_ip("10.0.0.9", "6.6.6.6", None, 2), "10.0.0.9")

    def test_single_entry_chain_with_depth_one(self):
        # Matches werkzeug ProxyFix(x_for=1) semantics: the single entry is the
        # address appended by the one trusted proxy. Only safe when the depth
        # is accurately configured and clients cannot reach the server directly.
        self.assertEqual(_resolve_client_ip("10.0.0.9", "6.6.6.6", None, 1), "6.6.6.6")

    def test_depth_two_picks_client_as_seen_by_edge_proxy(self):
        self.assertEqual(
            _resolve_client_ip("10.0.0.9", "6.6.6.6, 8.8.8.8, 9.9.9.9", None, 2),
            "8.8.8.8",
        )

    def test_negative_depth_trusts_whole_chain(self):
        # Documented special case: only safe when the outermost proxy strips
        # client-supplied X-Forwarded-For headers.
        self.assertEqual(
            _resolve_client_ip("10.0.0.9", "6.6.6.6, 9.9.9.9", None, -1), "6.6.6.6"
        )

    def test_x_real_ip_honored_when_proxied(self):
        self.assertEqual(
            _resolve_client_ip("10.0.0.9", None, "9.9.9.9", 2), "9.9.9.9"
        )

    def test_x_real_ip_ignored_when_not_proxied(self):
        self.assertEqual(
            _resolve_client_ip("10.0.0.9", None, "9.9.9.9", 0), "10.0.0.9"
        )

    def test_xff_takes_precedence_over_x_real_ip(self):
        self.assertEqual(
            _resolve_client_ip("10.0.0.9", "6.6.6.6, 9.9.9.9", "7.7.7.7", 1),
            "9.9.9.9",
        )

    def test_blank_xff_falls_through(self):
        self.assertEqual(
            _resolve_client_ip("10.0.0.9", "   ", "9.9.9.9", 1), "9.9.9.9"
        )
        self.assertEqual(_resolve_client_ip("10.0.0.9", " , ", None, 1), "10.0.0.9")

    def test_whitespace_is_stripped(self):
        self.assertEqual(
            _resolve_client_ip("10.0.0.9", "  6.6.6.6 , 9.9.9.9  ", None, 1),
            "9.9.9.9",
        )


class GetRealIpAddrTests(unittest.TestCase):
    """Tests for ``get_real_ip_addr`` honoring the configured depth."""

    def test_spoofed_identity_not_used_as_rate_limit_key(self):
        # Chain shorter than the declared depth: fail closed to the TCP peer.
        req = FakeRequest("10.0.0.9", {"X-Forwarded-For": "6.6.6.6"})
        with patch("delphi.epidata.server._common.REVERSE_PROXY_DEPTH", 2):
            self.assertEqual(get_real_ip_addr(req), "10.0.0.9")

    def test_well_configured_deployment_unchanged(self):
        req = FakeRequest("10.0.0.9", {"X-Forwarded-For": "6.6.6.6, 9.9.9.9"})
        with patch("delphi.epidata.server._common.REVERSE_PROXY_DEPTH", 1):
            self.assertEqual(get_real_ip_addr(req), "9.9.9.9")


if __name__ == "__main__":
    unittest.main()
