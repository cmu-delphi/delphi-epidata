"""Integration tests for delphi_epidata.py."""

# standard library
import unittest

# first party
from delphi.epidata.client.delphi_epidata import Epidata

# py3tester coverage target
__test_target__ = 'delphi.epidata.client.delphi_epidata'


class DelphiEpidataPythonClientTests(unittest.TestCase):
    """Tests the Python client."""

    def test_covidcast_happy_path(self):
        """Test that the covidcast endpoint returns expected data."""

        # Fetch data
        res = Epidata.covidcast(
            'fb-survey',
            'ili',
            'day',
            'county',
            [20200401, Epidata.range(20200405, 20200414)],
            '06001')

        # Check result
        self.assertEqual(res['result'], 1)
        self.assertEqual(res['message'], 'success')
        self.assertGreater(len(res['epidata']), 0)
        item = res['epidata'][0]
        self.assertIn('geo_value', item)
        self.assertIn('time_value', item)
        self.assertIn('direction', item)
        self.assertIn('value', item)
        self.assertIn('stderr', item)
        self.assertIn('sample_size', item)

    def test_covidcast_meta(self):
        """Test that the covidcast_meta endpoint returns expected data."""

        # Fetch data
        res = Epidata.covidcast_meta()

        # Check result
        self.assertEqual(res['result'], 1)
        self.assertEqual(res['message'], 'success')
        self.assertGreater(len(res['epidata']), 0)
        item = res['epidata'][0]
        self.assertIn('data_source', item)
        self.assertIn('time_type', item)
        self.assertIn('geo_type', item)
        self.assertIn('min_time', item)
        self.assertIn('max_time', item)
        self.assertIn('num_locations', item)
