"""Unit tests for database.py."""

# standard library
import unittest
from unittest.mock import MagicMock
from unittest.mock import sentinel

# first party
from delphi.epidata.acquisition.covid_hosp.common.test_utils import TestUtils
from delphi.epidata.acquisition.covid_hosp.state_timeseries.database import Database

# py3tester coverage target
__test_target__ = \
    'delphi.epidata.acquisition.covid_hosp.state_timeseries.database'


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
    self.assertEqual(mock_cursor.execute.call_count, 20)

    last_query_values = mock_cursor.execute.call_args[0][-1]
    expected_query_values = (
        0, sentinel.issue, 'MA', 20200510, 53, 84, 15691, 73, 12427, 83, 3625,
        84, None, 0, None, 0, None, 0, None, 0, None, 0, None, 0, None, 0,
        None, 0, None, 0, None, 0, None, 0, None, 0, 0.697850497273019, 72,
        10876, 15585, 0.2902550897239881, 83, 3607, 12427, 0.21056656682174496,
        73, 3304, 15691, None, None, None, None, None, None, None, None)
    self.assertEqual(len(last_query_values), len(expected_query_values))

    for actual, expected in zip(last_query_values, expected_query_values):
      self.assertAlmostEqual(actual, expected)
