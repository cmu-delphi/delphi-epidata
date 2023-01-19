"""Unit tests for utils.py."""

# standard library
from datetime import date
import unittest
from unittest.mock import MagicMock, PropertyMock, patch

# first party
from delphi.epidata.acquisition.covid_hosp.common.test_utils import UnitTestUtils
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils, CovidHospException

#third party
import pandas as pd

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covid_hosp.common.utils'


class UtilsTests(unittest.TestCase):

  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    self.test_utils = UnitTestUtils(__file__)

  def test_launch_if_main_when_main(self):
    """Launch the main entry point."""

    mock_entry = MagicMock()

    Utils.launch_if_main(mock_entry, '__main__')

    mock_entry.assert_called_once()

  def test_launch_if_main_when_not_main(self):
    """Don't launch the main entry point."""

    mock_entry = MagicMock()

    Utils.launch_if_main(mock_entry, '__test__')

    mock_entry.assert_not_called()

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

    issues = Utils.issues_to_fetch(test_metadata, pd.Timestamp("2021-3-13"), pd.Timestamp("2021-3-16"))
    self.assertEqual(issues,
                     {date(2021, 3, 14): [("b", pd.Timestamp("2021-03-14 00:00:00"))],
                      date(2021, 3, 15): [("c", pd.Timestamp("2021-03-15 00:00:00")),
                                          ("d", pd.Timestamp("2021-03-15 00:00:01"))]
                      }
                     )

  def test_run_skip_old_dataset(self):
    """Don't re-acquire an old dataset."""

    mock_network = MagicMock()
    mock_network.fetch_metadata.return_value = \
        self.test_utils.load_sample_metadata()
    mock_database = MagicMock()
    with mock_database.connect() as mock_connection:
      pass
    mock_connection.get_max_issue.return_value = pd.Timestamp("2200/1/1")

    result = Utils.update_dataset(database=mock_database, network=mock_network)

    self.assertFalse(result)
    mock_network.fetch_dataset.assert_not_called()
    mock_connection.insert_metadata.assert_not_called()
    mock_connection.insert_dataset.assert_not_called()

  def test_run_acquire_new_dataset(self):
    """Acquire a new dataset."""

    mock_network = MagicMock()
    mock_network.fetch_metadata.return_value = \
        self.test_utils.load_sample_metadata()
    fake_dataset = pd.DataFrame({"date": [pd.Timestamp("2020/1/1")], "state": ["ca"]})
    mock_network.fetch_dataset.return_value = fake_dataset
    mock_database = MagicMock()
    with mock_database.connect() as mock_connection:
      pass
    type(mock_connection).KEY_COLS = PropertyMock(return_value=["state", "date"])
    mock_connection.get_max_issue.return_value = pd.Timestamp("1900/1/1")
    with patch.object(Utils, 'issues_to_fetch') as mock_issues:
      mock_issues.return_value = {pd.Timestamp("2021/3/15"): [("url1", pd.Timestamp("2021-03-15 00:00:00")),
                                                              ("url2", pd.Timestamp("2021-03-15 00:00:00"))]}
      result = Utils.update_dataset(database=mock_database, network=mock_network)

    self.assertTrue(result)

    # should have been called twice
    mock_connection.insert_metadata.assert_called()
    assert mock_connection.insert_metadata.call_count == 2
    # most recent call should be for the final revision at url2
    args = mock_connection.insert_metadata.call_args[0]
    self.assertEqual(args[:2], (20210315, "url2"))
    pd.testing.assert_frame_equal(
      mock_connection.insert_dataset.call_args[0][1],
      pd.DataFrame({"state": ["ca"], "date": [pd.Timestamp("2020/1/1")]})
    )
    self.assertEqual(mock_connection.insert_dataset.call_args[0][0], 20210315)
