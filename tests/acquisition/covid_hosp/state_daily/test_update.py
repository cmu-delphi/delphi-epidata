"""Unit tests for update.py."""

# standard library
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import sentinel

# first party
from delphi.epidata.acquisition.covid_hosp.common.test_utils import TestUtils
from delphi.epidata.acquisition.covid_hosp.common.utils import Utils
from delphi.epidata.acquisition.covid_hosp.state_daily.update import Update
from delphi.epidata.acquisition.covid_hosp.state_daily.network import Network
from delphi.epidata.acquisition.covid_hosp.state_daily.database import Database

# py3tester coverage target
__test_target__ = \
    'delphi.epidata.acquisition.covid_hosp.state_daily.update'


class UpdateTests(unittest.TestCase):
  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    self.test_utils = TestUtils(__file__)

  def test_run(self):
    """Acquire a new dataset.

    This test is more involved than the other covid_hosp update tests because we
    need to make sure batches are being fetched properly.
    """

    mock_db = MagicMock(spec=Database)
    mock_db.contains_revision.return_value = False
    mock_db.get_max_issue.return_value = sentinel.last_issue
    sample_dataset = self.test_utils.load_sample_dataset()
    with patch.object(Network, 'fetch_metadata', return_value=self.test_utils.load_sample_metadata()) as mock_metadata, \
         patch.object(Utils, 'extract_resource_details', return_value=(sentinel.url, sentinel.revision)) as mock_details, \
         patch.object(Utils, 'get_issue_from_revision', return_value=sentinel.issue) as mock_issue, \
         patch.object(Database, 'connect', return_value=MagicMock()) as mock_connect, \
         patch.object(Network, 'fetch_revisions', return_value=[sentinel.batch]) as mock_revisions, \
         patch.object(Network, 'fetch_dataset', return_value=sample_dataset) as mock_fetch:
      # extra level of indirection due to context manager
      mock_connect.return_value.__enter__.return_value = mock_db

      result = Update.run()

      mock_metadata.assert_called_once()
      mock_details.assert_called_once()
      mock_issue.assert_called_with(sentinel.revision)
      mock_connect.assert_called_once()
      mock_revisions.assert_called_with(sentinel.last_issue)
      mock_fetch.assert_called_with(sentinel.url)
      self.assertEqual(mock_db.insert_metadata.call_args.args[0], sentinel.issue)
      self.assertEqual(mock_db.insert_metadata.call_args.args[1], sentinel.revision)
      mock_db.insert_dataset.assert_called_with(sentinel.issue, sample_dataset)
      self.assertEqual(result, True)
