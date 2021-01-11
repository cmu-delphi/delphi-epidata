"""Unit tests for update.py."""

# standard library
import unittest
from unittest import mock
from io import StringIO

# third party
import pandas as pd

# first party
from delphi.epidata.acquisition.covidcast_nowcast.load_sensors import main, load_and_prepare_file

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covidcast_nowcast.load_sensors'


class UpdateTests(unittest.TestCase):

  @mock.patch('time.time', mock.MagicMock(return_value=12345))
  def test_load_and_prepare_file(self):
    
    test_attributes = ("test_source",
                       "test_signal",
                       "test_time_type",
                       "test_geo_type",
                       "test_time_value",
                       "test_issue_value",
                       "test_lag_value")

    test_df = load_and_prepare_file(StringIO("geo_value,value\n01001,1.5"), test_attributes)
    pd.testing.assert_frame_equal(test_df,
                                  pd.DataFrame({"geo_value": ["01001"],
                                                "value": [1.5],
                                                "source": ["test_source"],
                                                "signal": ["test_signal"],
                                                "time_type": ["test_time_type"],
                                                "geo_type": ["test_geo_type"],
                                                "time_value": ["test_time_value"],
                                                "issue": ["test_issue_value"],
                                                "lag": ["test_lag_value"],
                                                "value_updated_timestamp": [12345]})
                                  )
