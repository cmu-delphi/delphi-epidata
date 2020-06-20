"""Unit tests for covidcast_meta_cache_updater.py."""

# standard library
import argparse
import json
import unittest
from unittest.mock import MagicMock

# third party
import pandas

# py3tester coverage target
__test_target__ = (
  'delphi.epidata.acquisition.covidcast.'
  'covidcast_meta_cache_updater'
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

    args = None
    mock_epidata_impl = MagicMock()
    mock_epidata_impl.covidcast_meta.return_value = api_response
    mock_database = MagicMock()
    mock_database.get_covidcast_meta.return_value=api_response['epidata']
    fake_database_impl = lambda: mock_database

    main(
        args,
        epidata_impl=mock_epidata_impl,
        database_impl=fake_database_impl)

    self.assertTrue(mock_database.connect.called)

    self.assertTrue(mock_database.update_covidcast_meta_cache.called)
    actual_args = mock_database.update_covidcast_meta_cache.call_args[0]
    expected_args = (json.dumps(api_response['epidata']),)
    self.assertEqual(actual_args, expected_args)

    self.assertTrue(mock_database.disconnect.called)
    self.assertTrue(mock_database.disconnect.call_args[0][0])

  def test_main_failure(self):
    """Run the main program with a query failure."""

    api_response = {
      'result': -123,
      'message': 'no',
    }

    args = None
    mock_database = MagicMock()
    mock_database.get_covidcast_meta.return_value = list()
    fake_database_impl = lambda: mock_database

    main(args, epidata_impl=None, database_impl=fake_database_impl)

    self.assertTrue(mock_database.get_covidcast_meta.called)
