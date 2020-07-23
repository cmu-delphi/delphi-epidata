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

  def test_main_successful(self):
    """Run the main program, and successfully commit changes."""

    args = None
    mock_database = MagicMock()
    fake_database_impl = lambda: mock_database
    mock_update_loop = MagicMock()

    main(
        args,
        database_impl=fake_database_impl,
        update_loop_impl=mock_update_loop)

    self.assertTrue(mock_update_loop.called)
    self.assertTrue(mock_database.connect.called)
    self.assertTrue(mock_database.disconnect.called)
    self.assertTrue(mock_database.disconnect.call_args[0][0])

  def test_main_unsuccessful(self):
    """Run the main program, but don't commit changes on failure."""

    args = None
    mock_database = MagicMock()
    fake_database_impl = lambda: mock_database
    mock_update_loop = MagicMock(side_effect=Exception('testing'))

    with self.assertRaises(Exception):
      main(
          args,
          database_impl=fake_database_impl,
          update_loop_impl=mock_update_loop)

    self.assertTrue(mock_update_loop.called)
    self.assertTrue(mock_database.connect.called)
    self.assertTrue(mock_database.disconnect.called)
    self.assertFalse(mock_database.disconnect.call_args[0][0])

  def test_update_loop(self):
    """Update direction for out-of-date covidcast rows."""

    mock_direction_impl = MagicMock()
    mock_direction_impl.scan_timeseries.return_value = ([10, 11], [20, 21])
    mock_database = MagicMock()
    mock_database.get_keys_with_potentially_stale_direction.return_value = [
      (
        'source',
        'signal',
        'geo_type',
        'geo_value',
        100,
        200,
        20200401,
        20200423,
        123,
      )
    ]
    mock_database.get_data_stdev_across_locations.return_value = [
      ('source', 'signal', 'geo_type', 456),
    ]
    mock_database.get_daily_timeseries_for_direction_update.return_value = [
      (1, 2, 3, 4, 5),
    ]

    update_loop(mock_database, direction_impl=mock_direction_impl)

    self.assertTrue(mock_direction_impl.scan_timeseries.called)
    args = mock_direction_impl.scan_timeseries.call_args[0]
    self.assertEqual(args[:-1], ([1], [2], [3], [4], [5]))

    # call the direction classifier
    get_direction_impl = args[-1]
    get_direction_impl('x', 'y')

    self.assertTrue(mock_direction_impl.get_direction.called)
    args, kwargs = mock_direction_impl.get_direction.call_args
    self.assertEqual(args, ('x', 'y'))
    expected_kwargs = {
      'n': Constants.SLOPE_STERR_SCALE,
      'limit': 456 * Constants.BASE_SLOPE_THRESHOLD,
    }
    self.assertEqual(kwargs, expected_kwargs)

    self.assertEqual(mock_database.update_direction.call_count, 2)
    call_args_list = mock_database.update_direction.call_args_list
    expected_args = (
      'source', 'signal', 'day', 'geo_type', 10, 'geo_value', 20,
    )
    self.assertEqual(call_args_list[0][0], expected_args)
    expected_args = (
      'source', 'signal', 'day', 'geo_type', 11, 'geo_value', 21,
    )
    self.assertEqual(call_args_list[1][0], expected_args)

    self.assertTrue(mock_database.update_timeseries_direction_updated_timestamp.called)
    args = mock_database.update_timeseries_direction_updated_timestamp.call_args[0]
    expected_args = ('source', 'signal', 'day', 'geo_type', 'geo_value')
    self.assertEqual(args, expected_args)
