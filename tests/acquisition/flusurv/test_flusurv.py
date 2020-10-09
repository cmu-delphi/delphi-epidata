"""Unit tests for flusurv.py."""

# standard library
import unittest
from unittest.mock import MagicMock
from unittest.mock import sentinel

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.flusurv.flusurv'


class FunctionTests(unittest.TestCase):
  """Tests each function individually."""

  def test_fetch_json(self):
    """Run through a successful flow."""

    path = 'path'
    payload = None

    response_object = MagicMock()
    response_object.status_code = 200
    response_object.headers = {'Content-Type': 'application/json'}
    response_object.json.return_value = sentinel.expected

    requests_impl = MagicMock()
    requests_impl.get.return_value = response_object

    actual = fetch_json(path, payload, requests_impl=requests_impl)

    self.assertEqual(actual, sentinel.expected)
