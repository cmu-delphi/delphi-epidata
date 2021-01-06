"""Unit tests for update.py."""

# standard library
import unittest
from unittest.mock import patch
from unittest.mock import sentinel
import tempfile
from io import StringIO

# third party
import pandas as pd

# first party
from delphi.epidata.acquisition.covidcast_nowcast.load_sensors import main, load_and_prepare_file

# py3tester coverage target
__test_target__ = 'delphi.epidata.acquisition.covidcast_nowcast.load_sensors'


class UpdateTests(unittest.TestCase):

  def test_load_and_prepate_file(self):
    
    test_attributes = ("test_source",
                       "test_signal",
                       "test_time_type",
                       "test_geo_type",
                       "test_time_value",
                       "test_issue_value",
                       "test_lag_value")

    test_df = load_and_prepare_file(StringIO("geo,value\n01001,1.5"), test_attributes)
    pd.testing.assert_frame_equal(test_df,
                                  pd.DataFrame({"geo":["01001"],
                                                "value": [1.5],
                                                "source": ["test_source"],
                                                "signal": ["test_signal"],
                                                "time_type": ["test_time_type"],
                                                "geo_type": ["test_geo_type"],
                                                "time_value": ["test_time_value"],
                                                "issue": ["test_issue_value"],
                                                "lag": ["test_lag_value"]})
                                  )
