"""Unit tests for network.py."""

# standard library
import unittest
from unittest.mock import MagicMock
from unittest.mock import sentinel

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covid_hosp.network'


class NetworkTests(unittest.TestCase):

  def test_fetch_metadata(self):
    """Fetch metadata as JSON."""

    mock_response = MagicMock()
    mock_response.json.return_value = sentinel.metadata
    mock_requests = MagicMock()
    mock_requests.get.return_value = mock_response

    result = Network.fetch_metadata(requests_impl=mock_requests)

    self.assertEqual(result, sentinel.metadata)
    mock_requests.get.assert_called_once_with(Network.METADATA_URL)

  def test_fetch_dataset(self):
    """Fetch dataset as CSV."""

    mock_pandas = MagicMock()
    mock_pandas.read_csv.return_value = sentinel.dataset

    result = Network.fetch_dataset(sentinel.url, pandas_impl=mock_pandas)

    self.assertEqual(result, sentinel.dataset)
    mock_pandas.read_csv.assert_called_once_with(sentinel.url)
