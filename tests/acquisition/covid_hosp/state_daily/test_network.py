"""Unit tests for network.py."""

# standard library
import requests
import unittest
from unittest.mock import patch
from unittest.mock import sentinel

# first party
from delphi.epidata.acquisition.covid_hosp.common.test_utils import UnitTestUtils
from delphi.epidata.acquisition.covid_hosp.state_daily.network import Network

# py3tester coverage target
__test_target__ = \
    'delphi.epidata.acquisition.covid_hosp.state_daily.network'


class NetworkTests(unittest.TestCase):
  def setUp(self):
    """Perform per-test setup."""

    # configure test data
    self.test_utils = UnitTestUtils(__file__)

  def test_fetch_metadata(self):
    """Fetch metadata as JSON."""

    with patch.object(Network, 'fetch_metadata_for_dataset') as func:
      func.return_value = sentinel.json

      result = Network.fetch_metadata()

      self.assertEqual(result, sentinel.json)
      func.assert_called_once_with(dataset_id=Network.DATASET_ID)

  def test_fetch_revisions(self):
    """Scrape CSV files from revision pages"""

    with patch.object(requests, 'get',
                      side_effect=list(self.test_utils.load_sample_revisions())) as requests_get:
      result = Network.fetch_revisions(20201210)

      # 4: one for the revisions page, and one for each of three qualifying
      # revisions details pages
      self.assertEqual(requests_get.call_count, 4)

      # The revisions page lists 5 revisions, but the first should be skipped
      # and the fifth should be excluded as outside the date range
      self.assertEqual(result, [
        "https://healthdata.gov/sites/default/files/reported_hospital_utilization_20210130_2344.csv",
        "https://healthdata.gov/sites/default/files/reported_hospital_utilization_20210129_1606.csv",
        "https://healthdata.gov/sites/default/files/reported_hospital_utilization_20210128_2205.csv"
      ])
