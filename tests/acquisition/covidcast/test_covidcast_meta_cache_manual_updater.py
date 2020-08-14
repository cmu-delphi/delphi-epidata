"""Unit tests for covidcast_meta_cache_manual_updater.py"""

# standard library
import argparse
import json
import unittest
from unittest.mock import MagicMock, patch, mock_open

# py3tester coverage target
__test_target__ = (
  'delphi.epidata.acquisition.covidcast.'
  'covidcast_meta_cache_manual_updater'
)


class UnitTests(unittest.TestCase):
  """Basic unit tests."""

  def test_get_argument_parser(self):
    """Return a parser for command-line arguments."""

    self.assertIsInstance(get_argument_parser(), argparse.ArgumentParser)

  def test_main_successful(self):
    """Run the main program successfully."""

    api_response = {
      'result': 1,
      'message': 'yes',
      'epidata': [{'foo': 'bar'}],
    }

    args = MagicMock(metadata="")
    mock_database = MagicMock()
    fake_database_impl = lambda: mock_database

    with patch('builtins.open', mock_open(read_data=json.dumps(api_response))):
        main(
            args,
            database_impl=fake_database_impl)

    self.assertTrue(mock_database.connect.called)

    self.assertTrue(mock_database.update_covidcast_meta_cache.called)
    actual_args = mock_database.update_covidcast_meta_cache.call_args[0]
    expected_args = (json.dumps(api_response['epidata']),)
    self.assertEqual(actual_args, expected_args)

    self.assertTrue(mock_database.disconnect.called)
    self.assertTrue(mock_database.disconnect.call_args[0][0])
