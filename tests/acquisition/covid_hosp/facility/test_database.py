"""Unit tests for database.py."""

# standard library
import unittest
from unittest.mock import MagicMock
from unittest.mock import sentinel

# first party
from delphi.epidata.acquisition.covid_hosp.common.test_utils import UnitTestUtils
from delphi.epidata.acquisition.covid_hosp.facility.database import Database

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covid_hosp.facility.database'


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

    result = database.insert_dataset(sentinel.publication_date, dataset)

    self.assertIsNone(result)
    self.assertEqual(mock_cursor.execute.call_count, 20)

    last_query_values = mock_cursor.execute.call_args[0][-1]
    expected_query_values = (
        0, sentinel.publication_date, '450822', 20201030,
        '6800 N MACARTHUR BLVD', 61.1, 7, 428, 60.9, 7, 426, 61.1, 7, 428,
        '450822', 'IRVING', '48113', '15', '6', 'MEDICAL CITY LAS COLINAS',
        'Short Term', 14.0, 7, 98, -999999.0, 7, -999999, 69.3, 7, 485, 69.0,
        7, 483, True, True, -999999, -999999, -999999, -999999, -999999,
        -999999, -999999, 7, 11, -999999, -999999, -999999, -999999, -999999,
        -999999, -999999, -999999, -999999, 16, -999999, -999999, -999999,
        -999999, 2, -999999, 11, -999999, 58, 536, 3, 8, 5, 17, 13, 10, 5.9,
        7, 41, -999999.0, 7, 16, -999999.0, 7, 14, 'TX', 6.9, 7, 48, 6.1, 7,
        43, 69.3, 7, 485, 14.3, 7, 100, -999999.0, 7, -999999, -999999.0, 7,
        -999999, -999999.0, 7, -999999, -999999.0, 7, -999999, 9, 18, 14, 0,
        1, 4, 6.1, 7, 43, '75039')
    self.assertEqual(len(last_query_values), len(expected_query_values))

    for actual, expected in zip(last_query_values, expected_query_values):
      self.assertAlmostEqual(actual, expected)
