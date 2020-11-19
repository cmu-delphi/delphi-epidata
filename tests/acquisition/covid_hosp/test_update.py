"""Unit tests for update.py."""

# standard library
from pathlib import Path
import unittest
from unittest.mock import MagicMock

# first party
from delphi.epidata.acquisition.covid_hosp.test_utils import TestUtils

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covid_hosp.update'


class UpdateTests(unittest.TestCase):

  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    path_to_repo_root = Path(__file__).parent.parent.parent.parent
    self.test_utils = TestUtils(path_to_repo_root)

  def test_get_entry_success(self):
    """Get a deeply nested field from an arbitrary object."""

    obj = self.test_utils.load_sample_metadata()

    result = Update.get_entry(obj, 'result', 0, 'tags', 2, 'id')

    self.assertEqual(result, '56f3cdad-8acb-46c8-bc71-aa1ded8407fb')

  def test_get_entry_failure(self):
    """Fail with a helpful message when a nested field doesn't exist."""

    obj = self.test_utils.load_sample_metadata()

    with self.assertRaises(UpdateException):
      Update.get_entry(obj, -1)

  def test_get_issue_from_revision(self):
    """Extract an issue date from a free-form revision string."""

    revisions = ('Tue, 11/03/2020 - 19:38', 'Mon, 11/16/2020 - 00:55', 'foo')
    issues = (20201103, 20201116, None)

    for revision, issue in zip(revisions, issues):
      with self.subTest(revision=revision):

        if issue:
          result = Update.get_issue_from_revision(revision)
          self.assertEqual(result, issue)
        else:
          with self.assertRaises(UpdateException):
            Update.get_issue_from_revision(revision)

  def test_get_date_as_int(self):
    """Convert a YYY-MM-DD date to a YYYYMMDD int."""

    result = Update.get_date_as_int('2020-11-17')

    self.assertEqual(result, 20201117)

  def test_extract_resource_details(self):
    """Extract URL and revision from metadata."""

    with self.subTest(name='invalid success'):
      metadata = self.test_utils.load_sample_metadata()
      metadata['success'] = False

      with self.assertRaises(UpdateException):
        Update.extract_resource_details(metadata)

    with self.subTest(name='invalid result'):
      metadata = self.test_utils.load_sample_metadata()
      metadata['result'] = []

      with self.assertRaises(UpdateException):
        Update.extract_resource_details(metadata)

    with self.subTest(name='invalid resource'):
      metadata = self.test_utils.load_sample_metadata()
      metadata['result'][0]['resources'] = []

      with self.assertRaises(UpdateException):
        Update.extract_resource_details(metadata)

    with self.subTest(name='valid'):
      metadata = self.test_utils.load_sample_metadata()

      url, revision = Update.extract_resource_details(metadata)

      expected_url = (
        'https://healthdata.gov/sites/default/files/'
        'reported_hospital_utilization_timeseries_20201115_2134.csv'
      )
      self.assertEqual(url, expected_url)
      self.assertEqual(revision, 'Mon, 11/16/2020 - 00:55')

  def test_run_skip_old_dataset(self):
    """Don't re-acquire an old dataset."""

    mock_network = MagicMock()
    mock_network.fetch_metadata.return_value = \
        self.test_utils.load_sample_metadata()
    mock_database = MagicMock()
    with mock_database.connect() as mock_connection:
      pass
    mock_connection.contains_revision.return_value = True

    result = Update.run(database_impl=mock_database, network_impl=mock_network)

    self.assertFalse(result)
    mock_network.fetch_dataset.assert_not_called()
    mock_connection.insert_metadata.assert_not_called()
    mock_connection.insert_dataset.assert_not_called()

  def test_run_acquire_new_dataset(self):
    """Acquire a new dataset."""

    mock_network = MagicMock()
    mock_network.fetch_metadata.return_value = \
        self.test_utils.load_sample_metadata()
    mock_network.fetch_dataset.return_value = \
        self.test_utils.load_sample_dataset()
    mock_database = MagicMock()
    with mock_database.connect() as mock_connection:
      pass
    mock_connection.contains_revision.return_value = False

    result = Update.run(database_impl=mock_database, network_impl=mock_network)

    self.assertTrue(result)

    mock_connection.insert_metadata.assert_called_once()
    args = mock_connection.insert_metadata.call_args[0]
    self.assertEqual(args[:2], (20201116, 'Mon, 11/16/2020 - 00:55'))

    mock_connection.insert_dataset.assert_called_once()
    args = mock_connection.insert_dataset.call_args[0]
    self.assertEqual(args[0], 20201116)
    self.assertEqual(len(args[1]), 20)
    self.assertEqual(args[1]['date'][19], 20200510)
