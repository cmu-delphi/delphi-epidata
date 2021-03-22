"""Unit tests for network.py."""

# standard library
import unittest
from unittest.mock import MagicMock, sentinel, patch

from delphi.epidata.acquisition.covid_hosp.common.network import Network

import pandas as pd

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covid_hosp.common.network'


class NetworkTests(unittest.TestCase):

  def test_fetch_metadata_for_dataset(self):
    """Fetch metadata as JSON."""

    with patch.object(pd, "read_csv") as func:
      func.return_value = pd.DataFrame(
        {"Archive Link": ["test2", "test1", "test3"],
         "Update Date": ["2020/1/2", "2020/1/1", "2020/1/3"]}
      )
      result = Network.fetch_metadata_for_dataset("test")
      pd.testing.assert_frame_equal(
        result,
        pd.DataFrame(
          {"Archive Link": ["test1", "test2", "test3"],
           "Update Date": pd.date_range("2020/1/1", "2020/1/3")}
        ).set_index("Update Date")
      )
      func.assert_called_once_with(
        "https://healthdata.gov/api/views/test/rows.csv",
        dtype=str
      )

  def test_fetch_dataset(self):
    """Fetch dataset as CSV."""

    mock_pandas = MagicMock()
    mock_pandas.read_csv.return_value = sentinel.dataset

    result = Network.fetch_dataset(sentinel.url, pandas_impl=mock_pandas)

    self.assertEqual(result, sentinel.dataset)
    mock_pandas.read_csv.assert_called_once_with(sentinel.url, dtype=str)
