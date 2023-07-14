"""Unit tests for database.py."""

# standard library
from datetime import date
import math
import unittest
from unittest.mock import MagicMock, patch, sentinel

# third party
import pandas as pd
import mysql.connector

# first party
from delphi.epidata.acquisition.covid_hosp.common.test_utils import TestDatabase
from delphi.epidata.common.covid_hosp.covid_hosp_schema_io import Columndef, CovidHospSomething

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covid_hosp.common.database'


class DatabaseTests(unittest.TestCase):

  def test_commit_and_close_on_success(self):
    """Commit and close the connection after success."""

    mock_connector = MagicMock()

    with TestDatabase.create_mock_database().connect(mysql_connector_impl=mock_connector) as database:
      connection = database.connection

    mock_connector.connect.assert_called_once()
    connection.commit.assert_called_once()
    connection.close.assert_called_once()

  def test_rollback_and_close_on_failure(self):
    """Rollback and close the connection after failure."""

    mock_connector = MagicMock()

    try:
      with TestDatabase.create_mock_database().connect(mysql_connector_impl=mock_connector) as database:
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
    mock_database = TestDatabase.create_mock_database()

    try:
      with patch.object(mysql.connector, 'connect', return_value=mock_connection), \
        mock_database.connect() as database:
        with database.new_cursor() as cursor:
          raise Exception('intentional test of exception handling')
    except Exception:
      pass

    mock_cursor.close.assert_called_once()

  def test_insert_metadata(self):
    """Add new metadata to the database."""

    # Note that query logic is tested separately by integration tests. This
    # test just checks that the function maps inputs to outputs as expected.

    mock_connection = MagicMock()
    mock_cursor = mock_connection.cursor()

    mock_database = TestDatabase.create_mock_database(table_name = sentinel.table_name, dataset_id = sentinel.hhs_dataset_id)

    with patch.object(mysql.connector, 'connect', return_value=mock_connection), \
      mock_database.connect() as database:
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

    mock_database = TestDatabase.create_mock_database(table_name = table_name, csv_cols=columns_and_types, issue_col='issue')

    dataset = pd.DataFrame.from_dict({
      'str_col': ['a', 'b', 'c', math.nan, 'e', 'f'],
      'int_col': ['1', '2', '3', '4', math.nan, '6'],
      'float_col': ['0.1', '0.2', '0.3', '0.4', '0.5', math.nan],
    })

    with patch.object(mysql.connector, 'connect', return_value=mock_connection), \
      mock_database.connect() as database:
      result = database.insert_dataset(sentinel.publication_date, dataset)

    self.assertIsNone(result)
    self.assertEqual(mock_cursor.executemany.call_count, 1)

    actual_sql = mock_cursor.executemany.call_args[0][0]
    self.assertIn(
      'INSERT INTO `test_table` (`id`, `issue`, `sql_str_col`, `sql_int_col`, `sql_float_col`)',
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

  def test_issues_to_fetch(self):
    test_metadata = pd.DataFrame({
      "date": [pd.Timestamp("2021-03-13 00:00:00"),
               pd.Timestamp("2021-03-14 00:00:00"),
               pd.Timestamp("2021-03-15 00:00:01"),
               pd.Timestamp("2021-03-15 00:00:00"),
               pd.Timestamp("2021-03-16 00:00:00")
               ],
      "Archive Link": ["a", "b", "d", "c", "e"]
    }).set_index("date")

    issues = TestDatabase.create_mock_database().issues_to_fetch(test_metadata, pd.Timestamp("2021-3-13"), pd.Timestamp("2021-3-16"))
    self.assertEqual(issues,
                     {date(2021, 3, 14): [("b", pd.Timestamp("2021-03-14 00:00:00"))],
                      date(2021, 3, 15): [("c", pd.Timestamp("2021-03-15 00:00:00")),
                                          ("d", pd.Timestamp("2021-03-15 00:00:01"))]
                      }
                     )