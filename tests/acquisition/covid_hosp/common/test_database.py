"""Unit tests for database.py."""

# standard library
import math
import unittest
from unittest.mock import MagicMock
from unittest.mock import sentinel

# third party
import pandas as pd

from delphi.epidata.acquisition.covid_hosp.common.columndef import Columndef
from delphi.epidata.acquisition.covid_hosp.common.database import Database
from delphi.epidata.common.covid_hosp.covid_hosp_schema_io import CovidHospSomething

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covid_hosp.common.database'

class TestDatabase(Database):
  DATASET_NAME = None


class TestDatabaseYAML(Database):
  DATASET_NAME = 'mock_dataset'


class DatabaseTests(unittest.TestCase):

  def test_commit_and_close_on_success(self):
    """Commit and close the connection after success."""

    mock_connector = MagicMock()

    with TestDatabase.connect(mysql_connector_impl=mock_connector) as database:
      connection = database.connection

    mock_connector.connect.assert_called_once()
    connection.commit.assert_called_once()
    connection.close.assert_called_once()

  def test_rollback_and_close_on_failure(self):
    """Rollback and close the connection after failure."""

    mock_connector = MagicMock()

    try:
      with TestDatabase.connect(mysql_connector_impl=mock_connector) as database:
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
    database = TestDatabase(mock_connection)

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

    chs = CovidHospSomething()
    chs.get_ds_table_name = MagicMock(return_value = sentinel.table_name)
    chs.get_ds_dataset_id = MagicMock(return_value = sentinel.hhs_dataset_id)
    chs.get_ds_ordered_csv_cols = MagicMock(return_value = None)
    chs.get_ds_key_cols = MagicMock(return_value = None)
    chs.get_ds_aggregate_key_cols = MagicMock(return_value = None)
    database = TestDatabaseYAML(mock_connection, chs=chs)

    with self.subTest(name='new revision'):
      mock_cursor.__iter__.return_value = [(0,)]

      result = database.contains_revision(sentinel.revision)

      # compare with boolean literal to test the type cast
      self.assertIs(result, False)
      query_values = mock_cursor.execute.call_args[0][-1]
      self.assertEqual(query_values, (sentinel.hhs_dataset_id, sentinel.revision))

    with self.subTest(name='old revision'):
      mock_cursor.__iter__.return_value = [(1,)]

      result = database.contains_revision(sentinel.revision)

      # compare with boolean literal to test the type cast
      self.assertIs(result, True)
      query_values = mock_cursor.execute.call_args[0][-1]
      self.assertEqual(query_values, (sentinel.hhs_dataset_id, sentinel.revision))

  def test_insert_metadata(self):
    """Add new metadata to the database."""

    # Note that query logic is tested separately by integration tests. This
    # test just checks that the function maps inputs to outputs as expected.

    mock_connection = MagicMock()
    mock_cursor = mock_connection.cursor()

    chs = CovidHospSomething()
    chs.get_ds_table_name = MagicMock(return_value = sentinel.table_name)
    chs.get_ds_dataset_id = MagicMock(return_value = sentinel.hhs_dataset_id)
    chs.get_ds_ordered_csv_cols = MagicMock(return_value = None)
    chs.get_ds_key_cols = MagicMock(return_value = None)
    chs.get_ds_aggregate_key_cols = MagicMock(return_value = None)
    database = TestDatabaseYAML(mock_connection, chs=chs)

    result = database.insert_metadata(
        sentinel.publication_date,
        sentinel.revision,
        sentinel.meta_json)

    self.assertIsNone(result)
    actual_values = mock_cursor.execute.call_args[0][-1]
    expected_values = (
      sentinel.table_name,
      sentinel.hhs_dataset_id,
      sentinel.publication_date,
      sentinel.revision,
      sentinel.meta_json,
    )
    self.assertEqual(actual_values, expected_values)

  def test_insert_dataset(self):
    """Add a new dataset to the database."""

    # Note that query logic is tested separately by integration tests. This
    # test just checks that the function maps inputs to outputs as expected.

    table_name = 'test_table'
    columns_and_types = [
      Columndef('str_col', 'sql_str_col', str),
      Columndef('int_col', 'sql_int_col', int),
      Columndef('float_col', 'sql_float_col', float),
    ]
    mock_connection = MagicMock()
    mock_cursor = mock_connection.cursor()

    chs = CovidHospSomething()
    chs.get_ds_table_name = MagicMock(return_value = table_name)
    chs.get_ds_dataset_id = MagicMock(return_value = None)
    chs.get_ds_ordered_csv_cols = MagicMock(return_value = columns_and_types)
    chs.get_ds_key_cols = MagicMock(return_value = None)
    chs.get_ds_aggregate_key_cols = MagicMock(return_value = None)
    database = TestDatabaseYAML(mock_connection, chs=chs)

    dataset = pd.DataFrame.from_dict({
      'str_col': ['a', 'b', 'c', math.nan, 'e', 'f'],
      'int_col': ['1', '2', '3', '4', math.nan, '6'],
      'float_col': ['0.1', '0.2', '0.3', '0.4', '0.5', math.nan],
    })

    result = database.insert_dataset(sentinel.publication_date, dataset)

    self.assertIsNone(result)
    self.assertEqual(mock_cursor.executemany.call_count, 1)

    actual_sql = mock_cursor.executemany.call_args[0][0]
    self.assertIn(
      'INSERT INTO `test_table` (`id`, `publication_date`, `sql_str_col`, `sql_int_col`, `sql_float_col`)',
      actual_sql)

    expected_values = [
      ('a', 1, 0.1),
      ('b', 2, 0.2),
      ('c', 3, 0.3),
      (None, 4, 0.4),
      ('e', None, 0.5),
      ('f', 6, None),
    ]

    for i, expected in enumerate(expected_values):
      with self.subTest(name=f'row {i + 1}'):
        # [0]: the first call() object
        # [0]: get positional args out of the call() object
        # [-1]: the last arg of the executemany call
        # [i]: the ith row inserted in the executemany
        actual = mock_cursor.executemany.call_args_list[0][0][-1][i]
        self.assertEqual(actual, (0, sentinel.publication_date) + expected)
