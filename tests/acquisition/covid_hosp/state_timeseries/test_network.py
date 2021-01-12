"""Unit tests for network.py."""

# standard library
import unittest
from unittest.mock import patch
from unittest.mock import sentinel

from delphi.epidata.acquisition.covid_hosp.state_timeseries.network import Network


# py3tester coverage target
__test_target__ = \
    'delphi.epidata.acquisition.covid_hosp.state_timeseries.network'


class NetworkTests(unittest.TestCase):

  def test_fetch_metadata(self):
    """Fetch metadata as JSON."""

    with patch.object(Network, 'fetch_metadata_for_dataset') as func:
      func.return_value = sentinel.json

      result = Network.fetch_metadata()

      self.assertEqual(result, sentinel.json)
      func.assert_called_once_with(dataset_id=Network.DATASET_ID)
