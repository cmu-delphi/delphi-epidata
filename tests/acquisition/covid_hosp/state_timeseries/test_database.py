"""Unit tests for database.py."""

# standard library
import unittest
from unittest.mock import MagicMock
from unittest.mock import sentinel

# first party
from delphi.epidata.acquisition.covid_hosp.common.test_utils import UnitTestUtils
from delphi.epidata.acquisition.covid_hosp.state_timeseries.database import Database

# py3tester coverage target
__test_target__ = \
    'delphi.epidata.acquisition.covid_hosp.state_timeseries.database'


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
        0, sentinel.issue, 'WY', 20200826, 0.0934579439252336, 26, 107, 10,
        0.4298245614035088, 28, 114, 49, 19, 7, 2, None, 4, 2, 0, 1, '2', 0, 26,
        3, 4, 0.0119465917076598, 26, 1423, 17, 1464, 28, 629, 28, 17, 26,
        0.4296448087431694, 28, 1464, 629, 5, 6, 7, 0.0275974025974025, 26, 616,
        17, 2, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 28,
        24, 25, 13, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
        41, 26, 42, 43, 44, 45, 0, 21, 0, 22, 46, 47, 48, 49, 50, 51, 52, 49,
        28, 10, 26, 7, 28, 17, 26, 14, 28, 53, 54, 55, 56, 0, 26, 0, 26,
        114, 28)
    self.assertEqual(len(last_query_values), len(expected_query_values))

    for actual, expected in zip(last_query_values, expected_query_values):
      if isinstance(expected, float):
        self.assertAlmostEqual(actual, expected)
      else:
        self.assertEqual(actual, expected)
