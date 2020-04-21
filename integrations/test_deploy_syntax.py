"""Simple integration test to validate the syntax of `deploy.json`."""

# standard library
import json
import unittest


class DeploySyntaxTests(unittest.TestCase):
  """Tests for `deploy.json`."""

  def test_syntax(self):
    """Ensure that `deploy.json` is valid JSON."""

    with open('repos/delphi/delphi-epidata/deploy.json', 'r') as f:
      self.assertIsInstance(json.loads(f.read()), dict)
