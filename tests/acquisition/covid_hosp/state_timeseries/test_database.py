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
    self.assertEqual(mock_cursor.execute.call_count, 22)

    last_query_values = mock_cursor.execute.call_args[0][-1]
    expected_query_values = (
        0, sentinel.issue, 'WY', 20200826, 0, 26, 1464,
        28, 629, 28, 17, 26, 2, 28, 13, 26, 0, 21, 0, 22, 49, 28, 10, 26, 7,
        28, 17, 26, 14, 28, 0, 26, 0, 26, 114, 28, 0.4296448087431694, 28, 629,
        1464, 0.027597402597402596, 26, 17, 616, 0.011946591707659873, 26, 17,
        1423, 0.09345794392523364, 26, 10, 107, 0.4298245614035088, 28, 49, 114,
        2, None, 4, 2, 19, 7, 'T')
    self.assertEqual(len(last_query_values), len(expected_query_values))

    for actual, expected in zip(last_query_values, expected_query_values):
      if isinstance(expected, float):
        self.assertAlmostEqual(actual, expected)
      else:
        self.assertEqual(actual, expected)
