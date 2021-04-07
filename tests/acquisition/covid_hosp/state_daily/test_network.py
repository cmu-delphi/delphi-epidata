"""Unit tests for network.py."""

# standard library
import requests
import unittest
from unittest.mock import patch
from unittest.mock import sentinel

# first party
from delphi.epidata.acquisition.covid_hosp.common.test_utils import TestUtils
from delphi.epidata.acquisition.covid_hosp.state_daily.network import Network

# third party
import pandas as pd

# py3tester coverage target
__test_target__ = \
    'delphi.epidata.acquisition.covid_hosp.state_daily.network'


class NetworkTests(unittest.TestCase):
  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    self.test_utils = TestUtils(__file__)

  def test_fetch_metadata(self):
    """Fetch metadata as JSON."""

    with patch.object(Network, 'fetch_metadata_for_dataset') as func:
      func.return_value = sentinel.json

      result = Network.fetch_metadata()

      self.assertEqual(result, sentinel.json)
      func.assert_called_once_with(dataset_id=Network.METADATA_ID)

  def test_fetch_revisions(self):
    """Scrape CSV files from revision pages"""

    test_metadata = pd.DataFrame(
      {"Archive Link": ["test1", "test2", "test3"]},
      index=pd.date_range("2020/1/1", "2020/1/3")
    )
    assert Network.fetch_revisions(test_metadata, pd.Timestamp("2020/1/1")) == ["test2", "test3"]