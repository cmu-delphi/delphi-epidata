"""Unit tests for direction_updater.py."""

# standard library
import argparse
import unittest
from unittest.mock import MagicMock

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covidcast.direction_updater'


class UnitTests(unittest.TestCase):
  """Basic unit tests."""

  def test_get_argument_parser(self):
    """Return a parser for command-line arguments."""

    self.assertIsInstance(get_argument_parser(), argparse.ArgumentParser)

  # TODO: this is temporary, will write test ASAP
  # def test_update_loop(self):
  #   """Update direction for out-of-date covidcast rows."""
  #
  #   self.assertTrue(False)

  def test_main_successful(self):
    """Run the main program and successfully commit changes."""

    args = MagicMock(test=False)
    mock_database = MagicMock()
    mock_database_impl = lambda: mock_database
    mock_update_loop = MagicMock()

    main(
        args=args,
        database_impl=mock_database_impl,
        update_loop_impl=mock_update_loop)

    self.assertTrue(mock_update_loop.called)
    self.assertTrue(mock_database.connect.called)
    self.assertTrue(mock_database.disconnect.called)
    self.assertTrue(mock_database.disconnect.call_args[0][0])

  def test_main_unsuccessful(self):
    """Run the main program but don't commit changes on failure."""

    args = MagicMock(test=False)
    mock_database = MagicMock()
    mock_database_impl = lambda: mock_database
    mock_update_loop = MagicMock(side_effect=Exception('testing'))

    with self.assertRaises(Exception):
      main(
          args=args,
          database_impl=mock_database_impl,
          update_loop_impl=mock_update_loop)

    self.assertTrue(mock_update_loop.called)
    self.assertTrue(mock_database.connect.called)
    self.assertTrue(mock_database.disconnect.called)
    self.assertFalse(mock_database.disconnect.call_args[0][0])

  def test_main_testing(self):
    """Run the main program but don't commit changes when testing."""

    args = MagicMock(test=True)
    mock_database = MagicMock()
    mock_database_impl = lambda: mock_database
    mock_update_loop = MagicMock()

    main(
        args=args,
        database_impl=mock_database_impl,
        update_loop_impl=mock_update_loop)

    self.assertTrue(mock_update_loop.called)
    self.assertTrue(mock_database.connect.called)
    self.assertTrue(mock_database.disconnect.called)
    actual_args = mock_database.disconnect.call_args[0]
    self.assertFalse(mock_database.disconnect.call_args[0][0])
