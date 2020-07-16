"""Unit tests for database.py."""

# standard library
import unittest
from unittest.mock import MagicMock

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covidcast.database'


class UnitTests(unittest.TestCase):
  """Basic unit tests."""

  def test_connect_opens_connection(self):
    """Connect to the database."""

    mock_connector = MagicMock()
    database = Database()

    database.connect(connector_impl=mock_connector)

    self.assertTrue(mock_connector.connect.called)

  def test_disconnect_with_rollback(self):
    """Disconnect from the database and rollback."""

    mock_connector = MagicMock()
    database = Database()
    database.connect(connector_impl=mock_connector)

    # rollback
    database.disconnect(False)

    connection = mock_connector.connect()
    self.assertFalse(connection.commit.called)
    self.assertTrue(connection.close.called)

  def test_disconnect_with_commit(self):
    """Disconnect from the database and commit."""

    mock_connector = MagicMock()
    database = Database()
    database.connect(connector_impl=mock_connector)

    # commit
    database.disconnect(True)

    connection = mock_connector.connect()
    self.assertTrue(connection.commit.called)
    self.assertTrue(connection.close.called)

  def test_count_all_rows_query(self):
    """Query to count all rows looks sensible.

    NOTE: Actual behavior is tested by integration test.
    """

    mock_connector = MagicMock()
    database = Database()
    database.connect(connector_impl=mock_connector)
    connection = mock_connector.connect()
    cursor = connection.cursor()
    cursor.__iter__.return_value = [(123,)]

    num = database.count_all_rows()

    self.assertEqual(num, 123)
    self.assertTrue(cursor.execute.called)

    sql = cursor.execute.call_args[0][0].lower()
    self.assertIn('select count(1)', sql)
    self.assertIn('from `covidcast`', sql)

  def test_insert_or_update_query(self):
    """Query to insert/update a row looks sensible.

    NOTE: Actual behavior is tested by integration test.
    """

    row = (
      'source',
      'signal',
      'time_type',
      'geo_type',
      'time_value',
      'geo_value',
      'value',
      'stderr',
      'sample_size',
      'issue',
      'lag',
    )
    mock_connector = MagicMock()
    database = Database()
    database.connect(connector_impl=mock_connector)

    database.insert_or_update(*row)

    connection = mock_connector.connect()
    cursor = connection.cursor()
    self.assertTrue(cursor.execute.called)

    sql, args = cursor.execute.call_args[0]
    self.assertEqual(args, row)

    sql = sql.lower()
    self.assertIn('insert into', sql)
    self.assertIn('`covidcast`', sql)
    self.assertIn('unix_timestamp', sql)
    self.assertIn('on duplicate key update', sql)

  def test_update_direction_query(self):
    """Query to update a row's `direction` looks sensible.

    NOTE: Actual behavior is tested by integration test.
    """

    args = (
      'source',
      'signal',
      'time_type',
      'geo_type',
      'time_value',
      'geo_value',
      'direction',
    )
    mock_connector = MagicMock()
    database = Database()
    database.connect(connector_impl=mock_connector)

    database.update_direction(*args)

    connection = mock_connector.connect()
    cursor = connection.cursor()
    self.assertTrue(cursor.execute.called)

    sql, args = cursor.execute.call_args[0]
    expected_args = (
      'direction',
      'source',
      'signal',
      'time_type',
      'geo_type',
      'time_value',
      'geo_value',
    )
    self.assertEqual(args, expected_args)

    sql = sql.lower()
    self.assertIn('update', sql)
    self.assertIn('`covidcast`', sql)
    self.assertIn('`timestamp2` = unix_timestamp', sql)
    self.assertIn('`direction` = %s', sql)

  def test_get_data_stdev_across_locations_query(self):
    """Query to get signal-level standard deviation looks sensible.

    NOTE: Actual behavior is tested by integration test.
    """

    args = ('max_day',)
    mock_connector = MagicMock()
    database = Database()
    database.connect(connector_impl=mock_connector)

    database.get_data_stdev_across_locations(*args)

    connection = mock_connector.connect()
    cursor = connection.cursor()
    self.assertTrue(cursor.execute.called)

    sql, args = cursor.execute.call_args[0]
    expected_args = ('max_day',)
    self.assertEqual(args, expected_args)

    sql = sql.lower()
    self.assertIn('select', sql)
    self.assertIn('`covidcast`', sql)
    self.assertIn('std(', sql)

  def test_get_keys_with_potentially_stale_direction_query(self):
    """Query to get time-series with stale `direction` looks sensible.

    NOTE: Actual behavior is tested by integration test.
    """

    mock_connector = MagicMock()
    database = Database()
    database.connect(connector_impl=mock_connector)

    database.get_keys_with_potentially_stale_direction()

    connection = mock_connector.connect()
    cursor = connection.cursor()
    self.assertTrue(cursor.execute.called)

    sql = cursor.execute.call_args[0][0].lower()
    self.assertIn('select', sql)
    self.assertIn('`covidcast`', sql)
    self.assertIn('timestamp1', sql)
    self.assertIn('timestamp2', sql)

  def test_get_daily_timeseries_for_direction_update_query(self):
    """Query to get a daily time-series looks sensible.

    NOTE: Actual behavior is tested by integration test.
    """

    args = ('source', 'signal', 'geo_type', 'geo_value', 'min_day', 'max_day')
    mock_connector = MagicMock()
    database = Database()
    database.connect(connector_impl=mock_connector)

    database.get_daily_timeseries_for_direction_update(*args)

    connection = mock_connector.connect()
    cursor = connection.cursor()
    self.assertTrue(cursor.execute.called)

    sql, args = cursor.execute.call_args[0]
    expected_args = (
      'min_day',
      'source',
      'signal',
      'geo_type',
      'geo_value',
      'min_day',
      'max_day',
    )
    self.assertEqual(args, expected_args)

    sql = sql.lower()
    self.assertIn('select', sql)
    self.assertIn('`covidcast`', sql)
    self.assertIn('timestamp1', sql)
    self.assertIn('timestamp2', sql)

  def test_update_timeseries_timestamp2_query(self):
    """Query to update the secondary timestamp of a time-series looks sensible.

    NOTE: Actual behavior is tested by integration test.
    """

    args = ('source', 'signal', 'time_type', 'geo_type', 'geo_value')
    mock_connector = MagicMock()
    database = Database()
    database.connect(connector_impl=mock_connector)

    database.update_timeseries_timestamp2(*args)

    connection = mock_connector.connect()
    cursor = connection.cursor()
    self.assertTrue(cursor.execute.called)

    sql, args = cursor.execute.call_args[0]
    expected_args = ('source', 'signal', 'time_type', 'geo_type', 'geo_value')
    self.assertEqual(args, expected_args)

    sql = sql.lower()
    self.assertIn('update', sql)
    self.assertIn('`covidcast`', sql)
    self.assertIn('timestamp2', sql)
    self.assertIn('unix_timestamp(now())', sql)

  def test_update_covidcast_meta_cache_query(self):
    """Query to update the metadata cache looks sensible.

    NOTE: Actual behavior is tested by integration test.
    """

    args = ('epidata_json',)
    mock_connector = MagicMock()
    database = Database()
    database.connect(connector_impl=mock_connector)

    database.update_covidcast_meta_cache(*args)

    connection = mock_connector.connect()
    cursor = connection.cursor()
    self.assertTrue(cursor.execute.called)

    sql, args = cursor.execute.call_args[0]
    expected_args = ('epidata_json',)
    self.assertEqual(args, expected_args)

    sql = sql.lower()
    self.assertIn('update', sql)
    self.assertIn('`covidcast_meta_cache`', sql)
    self.assertIn('timestamp', sql)
    self.assertIn('epidata', sql)
