"""Unit tests for utils.py."""

# standard library
import unittest
from unittest.mock import MagicMock
from unittest.mock import sentinel

# first party
from delphi.epidata.acquisition.covid_hosp.common.test_utils import TestUtils
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils, CovidHospException

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covid_hosp.common.utils'


class UtilsTests(unittest.TestCase):

  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    self.test_utils = TestUtils(__file__)

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

    mock_network = MagicMock()
    mock_network.fetch_metadata.return_value = \
        self.test_utils.load_sample_metadata()
    mock_database = MagicMock()
    with mock_database.connect() as mock_connection:
      pass
    mock_connection.contains_revision.return_value = True

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
    fake_dataset = [1, 2, 3]
    mock_network.fetch_dataset.return_value = fake_dataset
    mock_database = MagicMock()
    with mock_database.connect() as mock_connection:
      pass
    mock_connection.contains_revision.return_value = False

    result = Utils.update_dataset(database=mock_database, network=mock_network)

    self.assertTrue(result)

    mock_connection.insert_metadata.assert_called_once()
    args = mock_connection.insert_metadata.call_args[0]
    self.assertEqual(args[:2], (20210315, 'https://test.csv'))

    mock_connection.insert_dataset.assert_called_once_with(
        20210315, fake_dataset)
