"""Unit tests for database.py."""

# standard library
import unittest
from unittest.mock import MagicMock
from unittest.mock import sentinel

# first party
from delphi.epidata.acquisition.covid_hosp.common.test_utils import TestUtils
from delphi.epidata.acquisition.covid_hosp.facility.database import Database

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covid_hosp.facility.database'


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

    result = database.insert_dataset(sentinel.publication_date, dataset)

    self.assertIsNone(result)
    self.assertEqual(mock_cursor.execute.call_count, 20)

    last_query_values = mock_cursor.execute.call_args[0][-1]
    expected_query_values = (
        0, sentinel.publication_date, '450822', 20201030, 'TX', '450822',
        'MEDICAL CITY LAS COLINAS', '6800 N MACARTHUR BLVD', 'IRVING', '75039',
        'Short Term', '48113', True, 69.3, 61.1, 61.1, 69.0, 60.9, 6.9, 6.1,
        -999999, -999999, 69.3, 14.3, 6.1, 14.0, 5.9, -999999, -999999,
        -999999, -999999, -999999, 485, 428, 428, 483, 426, 48, 43, -999999,
        -999999, 485, 100, 43, 98, 41, 16, 14, -999999, -999999, -999999, 7, 7,
        7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 11, -999999,
        -999999, -999999, -999999, -999999, -999999, -999999, -999999, -999999,
        -999999, 58, -999999, -999999, -999999, -999999, -999999, -999999,
        -999999, -999999, -999999, -999999, -999999, 536, -999999)
    self.assertEqual(len(last_query_values), len(expected_query_values))

    for actual, expected in zip(last_query_values, expected_query_values):
      self.assertAlmostEqual(actual, expected)
