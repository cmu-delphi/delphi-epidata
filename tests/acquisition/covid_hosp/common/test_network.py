"""Unit tests for network.py."""

# standard library
import unittest
from unittest.mock import MagicMock
from unittest.mock import sentinel

from delphi.epidata.acquisition.covid_hosp.common.network import Network

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covid_hosp.common.network'


class NetworkTests(unittest.TestCase):

  def test_fetch_metadata_for_dataset(self):
    """Fetch metadata as JSON."""

    dataset_id = 'abc123'
    mock_response = MagicMock()
    mock_response.json.return_value = sentinel.metadata
    mock_requests = MagicMock()
    mock_requests.get.return_value = mock_response

    result = Network.fetch_metadata_for_dataset(
        dataset_id, requests_impl=mock_requests)

    self.assertEqual(result, sentinel.metadata)
    url = Network.METADATA_URL_TEMPLATE % dataset_id
    mock_requests.get.assert_called_once_with(url)

  def test_fetch_dataset(self):
    """Fetch dataset as CSV."""

    mock_pandas = MagicMock()
    mock_pandas.read_csv.return_value = sentinel.dataset

    result = Network.fetch_dataset(sentinel.url, pandas_impl=mock_pandas)

    self.assertEqual(result, sentinel.dataset)
    mock_pandas.read_csv.assert_called_once_with(sentinel.url, dtype=str)
