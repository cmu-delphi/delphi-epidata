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

    with patch.object(pd, "read_csv") as func:
      func.return_value = pd.DataFrame(
        {"Archive Link": ["test2", "test1", "test3"],
         "Update Date": ["2020/1/2", "2020/1/1", "2020/1/3"]}
      )
      result = Network.fetch_metadata()
      pd.testing.assert_frame_equal(
        result,
        pd.DataFrame(
          {"Archive Link": ["test1", "test2", "test3"],
           "Update Date": pd.date_range("2020/1/1", "2020/1/3")}
        ).set_index("Update Date")
      )
      func.assert_called_once_with(
        "https://healthdata.gov/api/views/%s/rows.csv" % Network.DATASET_ID,
        dtype=str
      )

  def test_fetch_revisions(self):
    """Scrape CSV files from revision pages"""

    test_metadata = pd.DataFrame(
      {"Archive Link": ["test1", "test2", "test3"]},
      index=pd.date_range("2020/1/1", "2020/1/3")
    )
    assert Network.fetch_revisions(test_metadata, pd.Timestamp("2020/1/1")) == ["test2", "test3"]