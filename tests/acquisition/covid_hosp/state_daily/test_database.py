"""Unit tests for database.py."""

# standard library
import unittest
from unittest.mock import MagicMock
from unittest.mock import sentinel

# first party
from delphi.epidata.acquisition.covid_hosp.state_daily.database import Database
from delphi.epidata.acquisition.covid_hosp.common.test_utils import UnitTestUtils

import pandas as pd

# py3tester coverage target
__test_target__ = \
    'delphi.epidata.acquisition.covid_hosp.state_daily.database'


class DatabaseTests(unittest.TestCase):

  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    self.test_utils = UnitTestUtils(__file__)

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
    self.assertEqual(mock_cursor.executemany.call_count, 1)

    last_query_values = mock_cursor.executemany.call_args[0][-1][-1]
    expected_query_values = (
        0, sentinel.issue,  'WY', 20201209,
        0.2519685039370078, 29, 127, 32, 0.4233576642335766, 31, 137, 58, 22, 2,
        7, None, 2, 8, 0, 1, '2', 5, 29, 3, 4, 0.1172985781990521, 29, 1688, 198,
        1729, 31, 856, 31, 198, 29, 0.4950838635049161, 31, 1729, 856, 5, 6, 7,
        0.2362768496420047, 29, 838, 198, 26, 8, 9, 10, 11, 12, 13, 14, 15, 16,
        17, 18, 19, 20, 21, 22, 23, 31, 24, 25, 15, 26, 27, 28, 29, 30, 31, 32,
        33, 34, 35, 36, 37, 38, 39, 40, 41, 29, 42, 43, 44, 45, 0, 29, 0, 29,
        46, 47, 48, 49, 50, 51, 52, 58, 31, 32, 29, 32, 31, 196, 29, 189, 31,
        53, 54, 55, 56, 2, 29, 2, 29, 137, 31, 'D')
    self.assertEqual(len(last_query_values), len(expected_query_values))

    for actual, expected in zip(last_query_values, expected_query_values):
      if isinstance(expected, float):
        self.assertAlmostEqual(actual, expected)
      else:
        self.assertEqual(actual, expected)

  def test_max_issue(self):
    """Get the most recent issue added to the database"""

    # Note that query logic is tested separately by integration tests. This
    # test just checks that the function maps inputs to outputs as expected.

    mock_connection = MagicMock()
    mock_cursor = mock_connection.cursor()
    database = Database(mock_connection)

    result = database.get_max_issue()

    self.assertEqual(mock_cursor.execute.call_count, 1)
    self.assertEqual(result, pd.Timestamp("1900/1/1"), "max issue when db is empty")
