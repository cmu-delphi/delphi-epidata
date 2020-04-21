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
    """Query to count all rows is reasonable.

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
    """Query to insert/update a row is reasonable.

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
    )
    mock_connector = MagicMock()
    database = Database()
    database.connect(connector_impl=mock_connector)

    database.insert_or_update(*row)

    connection = mock_connector.connect()
    cursor = connection.cursor()
    self.assertTrue(cursor.execute.called)

    sql, args = cursor.execute.call_args[0]
    sql = sql.lower()
    self.assertIn('insert into `covidcast` values', sql)
    self.assertIn('on duplicate key update', sql)
    self.assertEqual(args, row)
