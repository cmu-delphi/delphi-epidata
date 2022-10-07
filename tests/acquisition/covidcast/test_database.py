"""Unit tests for database.py."""

# standard library
import unittest
from unittest.mock import MagicMock

from delphi.epidata.acquisition.covidcast.database import Database

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

  def test_insert_or_update_batch_exception_reraised(self):
    """Test that an exception is reraised"""
    mock_connector = MagicMock()
    database = Database()
    database.connect(connector_impl=mock_connector)
    connection = mock_connector.connect()
    cursor = connection.cursor() 
    cursor.executemany.side_effect = Exception('Test')

    cc_rows = {MagicMock(geo_id='CA', val=1, se=0, sample_size=0)}
    self.assertRaises(Exception, database.insert_or_update_batch, cc_rows)
  
  def test_insert_or_update_batch_row_count_returned(self):
    """Test that the row count is returned"""
    mock_connector = MagicMock()
    database = Database()
    database.count_all_load_rows = lambda:0 # simulate an empty load table
    database.connect(connector_impl=mock_connector)
    connection = mock_connector.connect()
    cursor = connection.cursor() 
    cursor.rowcount = 3

    cc_rows = [MagicMock(geo_id='CA', val=1, se=0, sample_size=0)]
    result = database.insert_or_update_batch(cc_rows)
    self.assertEqual(result, 3)

  def test_insert_or_update_batch_none_returned(self):
    """Test that None is returned when row count cannot be returned"""
    mock_connector = MagicMock()
    database = Database()
    database.count_all_load_rows = lambda:0 # simulate an empty load table
    database.connect(connector_impl=mock_connector)
    connection = mock_connector.connect()
    cursor = connection.cursor() 
    cursor.rowcount = -1

    cc_rows = [MagicMock(geo_id='CA', val=1, se=0, sample_size=0)]
    result = database.insert_or_update_batch(cc_rows)
    self.assertIsNone(result)
