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

  def test_update_loop(self):
    """Update direction for out-of-date covidcast rows."""

    batch1 = [
      (
        'a',
        'b',
        'day',
        'state',
        20200421,
        'ca',
        100,
        200,
        300,
      ), (
        'a',
        'b',
        'day',
        'state',
        20200421,
        'tx',
        100,
        200,
        1,  # not enough history to compute direction
      ),
    ]
    batch2 = [
      (
        'c',
        'd',
        'day',
        'state',
        20200421,
        'ca',
        100,
        200,
        300,
      ), (
        'c',
        'd',
        'day',
        'state',
        20200421,
        'tx',
        100,
        200,
        300,
      ),
    ]
    batches = [batch1, batch2, []]

    def get_rows_to_compute_direction(*args):
      if args == ('a', 'b', 'state', 20200421, 'ca'):
        return [(1, 1)]
      if args == ('c', 'd', 'state', 20200421, 'ca'):
        return [(2, 2)]
      if args == ('c', 'd', 'state', 20200421, 'tx'):
        return [(3, 3)]
      # fail the test at this point
      raise Exception('unexpected row')

    mock_database = MagicMock()
    mock_database.get_rows_with_stale_direction.side_effect = batches
    mock_database.get_rows_to_compute_direction = get_rows_to_compute_direction
    mock_direction = MagicMock()
    mock_direction.get_direction.side_effect = [1, 2, 3]

    update_loop(mock_database, direction_impl=mock_direction)

    self.assertEqual(mock_direction.get_direction.call_count, 3)
    call_args_list = mock_direction.get_direction.call_args_list
    self.assertEqual(call_args_list[0][0], ([1], [1]))
    self.assertEqual(call_args_list[1][0], ([2], [2]))
    self.assertEqual(call_args_list[2][0], ([3], [3]))

    self.assertEqual(mock_database.update_direction.call_count, 4)
    call_args_list = mock_database.update_direction.call_args_list
    expected = ('a', 'b', 'day', 'state', 20200421, 'ca', 1)
    self.assertEqual(call_args_list[0][0], expected)
    expected = ('a', 'b', 'day', 'state', 20200421, 'tx', None)
    self.assertEqual(call_args_list[1][0], expected)
    expected = ('c', 'd', 'day', 'state', 20200421, 'ca', 2)
    self.assertEqual(call_args_list[2][0], expected)
    expected = ('c', 'd', 'day', 'state', 20200421, 'tx', 3)
    self.assertEqual(call_args_list[3][0], expected)

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
