"""Unit tests for update.py."""

# standard library
import unittest
from unittest import mock
from io import StringIO

# third party
import pandas as pd

# first party
from delphi.epidata.acquisition.covidcast.csv_importer import PathDetails
from delphi.epidata.acquisition.covidcast_nowcast.load_sensors import main, load_and_prepare_file

# py3tester coverage target
__test_target__ = "delphi.epidata.acquisition.covidcast_nowcast.load_sensors"


class UpdateTests(unittest.TestCase):
    @mock.patch("time.time", mock.MagicMock(return_value=12345))
    def test_load_and_prepare_file(self):

        test_attributes = PathDetails(
            20210102,
            3,
            "test_source",
            "test_signal",
            "test_time_type",
            20201231,
            "test_geo_type",
        )

        test_df = load_and_prepare_file(
            StringIO("sensor_name,geo_value,value\ntestname,01001,1.5"), test_attributes
        )
        pd.testing.assert_frame_equal(
            test_df,
            pd.DataFrame(
                {
                    "sensor_name": ["testname"],
                    "geo_value": ["01001"],
                    "value": [1.5],
                    "source": ["test_source"],
                    "signal": ["test_signal"],
                    "time_type": ["test_time_type"],
                    "geo_type": ["test_geo_type"],
                    "time_value": [20201231],
                    "issue": [20210102],
                    "lag": [3],
                    "value_updated_timestamp": [12345],
                }
            ),
        )
