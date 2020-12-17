"""Unit tests for database.py."""

# standard library
import unittest
from unittest.mock import MagicMock
from unittest.mock import sentinel

# first party
from delphi.epidata.acquisition.covid_hosp.common.test_utils import TestUtils

# py3tester coverage target
__test_target__ = \
    'delphi.epidata.acquisition.covid_hosp.state_daily.database'


class DatabaseTests(unittest.TestCase):

  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    self.test_utils = TestUtils(__file__)

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
    self.assertEqual(mock_cursor.execute.call_count, 53)

    last_query_values = mock_cursor.execute.call_args[0][-1]
    expected_query_values = (
        0, sentinel.issue, 'WY',  20201209, 8, 21, 2, 7, 22, 2, 5, 29, 1729,
        31, 856, 31, 198, 29, 26, 31, 15, 29, 0, 29, 0, 29, 58, 31, 32, 29,
        32, 31, 196, 29, 189, 31, 2, 29, 2, 29, 137, 31, 0.4950838635049161, 31,
        856, 1729, 0.23627684964200477, 29, 198, 838, 0.11729857819905214,
        29, 198, 1688, 0.25196850393700787, 29, 32, 127, 0.4233576642335766,
        31, 58, 137, 'D')
    self.assertEqual(len(last_query_values), len(expected_query_values))

    for actual, expected in zip(last_query_values, expected_query_values):
      if isinstance(expected, float):
        self.assertAlmostEqual(actual, expected)
      else:
        self.assertEqual(actual, expected)
