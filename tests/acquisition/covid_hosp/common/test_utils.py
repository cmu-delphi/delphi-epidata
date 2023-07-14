"""Unit tests for utils.py."""

# standard library
import unittest
from unittest.mock import MagicMock, patch

# first party
from delphi.epidata.acquisition.covid_hosp.common.network import Network
from delphi.epidata.acquisition.covid_hosp.common.test_utils import TestDatabase, UnitTestUtils
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils, CovidHospException
from delphi.epidata.common.covid_hosp.covid_hosp_schema_io import CovidHospSomething

#third party
import pandas as pd
import mysql.connector

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covid_hosp.common.utils'

class UtilsTests(unittest.TestCase):

  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    self.test_utils = UnitTestUtils(__file__)

  def test_int_from_date(self):
    """Convert a YYY-MM-DD date to a YYYYMMDD int."""

    self.assertEqual(Utils.int_from_date('2020-11-17'), 20201117)
    self.assertEqual(Utils.int_from_date('2020/11/17'), 20201117)
    self.assertEqual(Utils.int_from_date('2020/11/17 10:00:00'), 20201117)

  def test_parse_bool(self):
    """Parse a boolean value from a string."""

    with self.subTest(name='None'):
      self.assertIsNone(Utils.parse_bool(None))

    with self.subTest(name='empty'):
      self.assertIsNone(Utils.parse_bool(''))

    with self.subTest(name='true'):
      self.assertTrue(Utils.parse_bool('true'))
      self.assertTrue(Utils.parse_bool('True'))
      self.assertTrue(Utils.parse_bool('tRuE'))

    with self.subTest(name='false'):
      self.assertFalse(Utils.parse_bool('false'))
      self.assertFalse(Utils.parse_bool('False'))
      self.assertFalse(Utils.parse_bool('fAlSe'))

    with self.subTest(name='exception'):
      with self.assertRaises(CovidHospException):
        Utils.parse_bool('maybe')
  def test_run_skip_old_dataset(self):
    """Don't re-acquire an old dataset."""

    mock_connection = MagicMock()
    with patch.object(Network, 'fetch_metadata', return_value=self.test_utils.load_sample_metadata()), \
         patch.object(Network, 'fetch_dataset', return_value=None) as fetch_dataset, \
         patch.object(mysql.connector, 'connect', return_value=mock_connection), \
         patch.object(TestDatabase, 'get_max_issue', return_value=pd.Timestamp("2200/1/1")), \
         patch.object(TestDatabase, 'insert_metadata', return_value=None) as insert_metadata, \
         patch.object(TestDatabase, 'insert_dataset', return_value=None) as insert_dataset:
      result = TestDatabase.create_mock_database().update_dataset()

    self.assertFalse(result)
    fetch_dataset.assert_not_called()
    insert_metadata.assert_not_called()
    insert_dataset.assert_not_called()

  def test_run_acquire_new_dataset(self):
    """Acquire a new dataset."""

    mock_connection = MagicMock()
    fake_dataset = pd.DataFrame({"date": [pd.Timestamp("2020/1/1")], "state": ["ca"]})
    fake_issues = {pd.Timestamp("2021/3/15"): [("url1", pd.Timestamp("2021-03-15 00:00:00")),
                                              ("url2", pd.Timestamp("2021-03-15 00:00:00"))]}

    with patch.object(Network, 'fetch_metadata', return_value=self.test_utils.load_sample_metadata()), \
         patch.object(Network, 'fetch_dataset', return_value=fake_dataset), \
         patch.object(CovidHospSomething, 'get_ds_table_name', return_value=None), \
         patch.object(CovidHospSomething, 'get_ds_dataset_id', return_value=None), \
         patch.object(CovidHospSomething, 'get_ds_metadata_id', return_value=None), \
         patch.object(CovidHospSomething, 'get_ds_issue_column', return_value=None), \
         patch.object(CovidHospSomething, 'get_ds_ordered_csv_cols', return_value=[]), \
         patch.object(CovidHospSomething, 'get_ds_key_cols', return_value=["state", "date"]), \
         patch.object(CovidHospSomething, 'get_ds_aggregate_key_cols', return_value=None), \
         patch.object(mysql.connector, 'connect', return_value=mock_connection), \
         patch.object(TestDatabase, 'get_max_issue', return_value=pd.Timestamp("1900/1/1")), \
         patch.object(TestDatabase, 'issues_to_fetch', return_value=fake_issues), \
         patch.object(TestDatabase, 'insert_metadata', return_value=None) as insert_metadata, \
         patch.object(TestDatabase, 'insert_dataset', return_value=None) as insert_dataset:
        result = TestDatabase().update_dataset()

    self.assertTrue(result)

    # should have been called twice
    insert_metadata.assert_called()
    assert insert_metadata.call_count == 2
    # most recent call should be for the final revision at url2
    args = insert_metadata.call_args[0]
    self.assertEqual(args[:2], (20210315, "url2"))
    pd.testing.assert_frame_equal(
      insert_dataset.call_args[0][1],
      pd.DataFrame({"state": ["ca"], "date": [pd.Timestamp("2020/1/1")]})
    )
    self.assertEqual(insert_dataset.call_args[0][0], 20210315)
