"""Unit tests for database.py."""

# standard library
import unittest
from unittest.mock import MagicMock
from unittest.mock import sentinel

# first party
from delphi.epidata.acquisition.covid_hosp.state_timeseries.test_utils import TestUtils

# py3tester coverage target
__test_target__ = \
    'delphi.epidata.acquisition.covid_hosp.state_timeseries.database'


class DatabaseTests(unittest.TestCase):

  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    self.test_utils = TestUtils(__file__)

  def test_commit_and_close_on_success(self):
    """Commit and close the connection after success."""

    mock_connector = MagicMock()

    with Database.connect(mysql_connector_impl=mock_connector) as database:
      connection = database.connection

    mock_connector.connect.assert_called_once()
    connection.commit.assert_called_once()
    connection.close.assert_called_once()

  def test_rollback_and_close_on_failure(self):
    """Rollback and close the connection after failure."""

    mock_connector = MagicMock()

    try:
      with Database.connect(mysql_connector_impl=mock_connector) as database:
        connection = database.connection
        raise Exception('intentional test of exception handling')
    except Exception:
      pass

    mock_connector.connect.assert_called_once()
    connection.commit.assert_not_called()
    connection.close.assert_called_once()

  def test_new_cursor_cleanup(self):
    """Cursors are unconditionally closed."""

    mock_connection = MagicMock()
    mock_cursor = mock_connection.cursor()
    database = Database(mock_connection)

    try:
      with database.new_cursor() as cursor:
        raise Exception('intentional test of exception handling')
    except Exception:
      pass

    mock_cursor.close.assert_called_once()

  def test_contains_revision(self):
    """Check whether a revision is already in the database."""

    # Note that query logic is tested separately by integration tests. This
    # test just checks that the function maps inputs to outputs as expected.

    mock_connection = MagicMock()
    mock_cursor = mock_connection.cursor()
    database = Database(mock_connection)

    with self.subTest(name='new revision'):
      mock_cursor.__iter__.return_value = [(0,)]

      result = database.contains_revision(sentinel.revision)

      # compare with boolean literal to test the type cast
      self.assertIs(result, False)
      query_values = mock_cursor.execute.call_args[0][-1]
      self.assertEqual(query_values, (sentinel.revision,))

    with self.subTest(name='old revision'):
      mock_cursor.__iter__.return_value = [(1,)]

      result = database.contains_revision(sentinel.revision)

      # compare with boolean literal to test the type cast
      self.assertIs(result, True)
      query_values = mock_cursor.execute.call_args[0][-1]
      self.assertEqual(query_values, (sentinel.revision,))

  def test_insert_metadata(self):
    """Add new metadata to the database."""

    # Note that query logic is tested separately by integration tests. This
    # test just checks that the function maps inputs to outputs as expected.

    mock_connection = MagicMock()
    mock_cursor = mock_connection.cursor()
    database = Database(mock_connection)

    result = database.insert_metadata(
        sentinel.issue, sentinel.revision, sentinel.meta_json)

    self.assertIsNone(result)
    query_values = mock_cursor.execute.call_args[0][-1]
    self.assertEqual(
        query_values, (sentinel.issue, sentinel.revision, sentinel.meta_json))

  def test_insert_dataset(self):
    """Add a new dataset to the database."""

    # Note that query logic is tested separately by integration tests. This
    # test just checks that the function maps inputs to outputs as expected.

    mock_connection = MagicMock()
    mock_cursor = mock_connection.cursor()
    database = Database(mock_connection)
    dataset = self.test_utils.load_sample_dataset()

    result = database.insert_dataset(sentinel.issue, dataset)

    self.assertIsNone(result)
    self.assertEqual(mock_cursor.execute.call_count, 20)

    last_query_values = mock_cursor.execute.call_args[0][-1]
    expected_query_values = (
        0, sentinel.issue, 'MA', '2020-05-10', 53, 84, 15691, 73, 12427, 83,
        3625, 84, None, 0, None, 0, None, 0, None, 0, None, 0, None, 0, None,
        0, None, 0, None, 0, None, 0, None, 0, None, 0, 0.697850497273019, 72,
        10876, 15585, 0.2902550897239881, 83, 3607, 12427, 0.21056656682174496,
        73, 3304, 15691, None, None, None, None, None, None, None, None)
    self.assertEqual(len(last_query_values), len(expected_query_values))

    for actual, expected in zip(last_query_values, expected_query_values):
      if isinstance(expected, float):
        self.assertAlmostEqual(actual, expected)
      else:
        self.assertEqual(actual, expected)
