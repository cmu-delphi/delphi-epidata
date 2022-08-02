import unittest

from pandas import DataFrame, date_range
from pandas.testing import assert_frame_equal

from delphi_utils.nancodes import Nans
from ....src.server.utils.dates import date_to_time_value
from ....src.acquisition.covidcast.covidcast_row import set_df_dtypes, transpose_dict, CovidcastRow, CovidcastRows

class TestCovidcastRows(unittest.TestCase):
    def test_transpose_dict(self):
        assert transpose_dict(dict([["a", [2, 4, 6]], ["b", [3, 5, 7]], ["c", [10, 20, 30]]])) == [{"a": 2, "b": 3, "c": 10}, {"a": 4, "b": 5, "c": 20}, {"a": 6, "b": 7, "c": 30}]

    def test_CovidcastRow(self):
        df = CovidcastRow(value=5.0).api_row_df
        expected_df = DataFrame.from_records([{
            "source": "src",
            "signal": "sig",
            "geo_type": "county",
            "time_value": 20200202,
            "geo_value": "01234",
            "value": 5.0,
            "stderr": 10.0,
            "sample_size": 10.0,
            "missing_value": Nans.NOT_MISSING,
            "missing_stderr": Nans.NOT_MISSING,
            "missing_sample_size": Nans.NOT_MISSING,
            "issue": 20200202,
            "lag": 0,
        }])
        assert_frame_equal(df, expected_df)

        df = CovidcastRow(value=5.0).api_compatibility_row_df
        expected_df = DataFrame.from_records([{
            "signal": "sig",
            "geo_type": "county",
            "time_value": 20200202,
            "geo_value": "01234",
            "value": 5.0,
            "stderr": 10.0,
            "sample_size": 10.0,
            "missing_value": Nans.NOT_MISSING,
            "missing_stderr": Nans.NOT_MISSING,
            "missing_sample_size": Nans.NOT_MISSING,
            "issue": 20200202,
            "lag": 0,
        }])
        assert_frame_equal(df, expected_df)

    def test_CovidcastRows(self):
        df = CovidcastRows.from_args(signal=["sig_base"] * 5 + ["sig_other"] * 5, time_value=date_range("2021-05-01", "2021-05-05").to_list() * 2, value=list(range(10))).api_row_df
        expected_df = set_df_dtypes(DataFrame({
            "source": ["src"] * 10,
            "signal": ["sig_base"] * 5 + ["sig_other"] * 5,
            "geo_type": ["county"] * 10,
            "time_value": map(date_to_time_value, date_range("2021-05-01", "2021-05-5").to_list() * 2),
            "geo_value": ["01234"] * 10,
            "value": range(10),
            "stderr": [10.0] * 10,
            "sample_size": [10.0] * 10,
            "missing_value": [Nans.NOT_MISSING] * 10,
            "missing_stderr": [Nans.NOT_MISSING] * 10,
            "missing_sample_size": [Nans.NOT_MISSING] * 10,
            "issue": map(date_to_time_value, date_range("2021-05-01", "2021-05-5").to_list() * 2),
            "lag": [0] * 10,
        }), CovidcastRows()._DTYPES)
        assert_frame_equal(df, expected_df)

        df = CovidcastRows.from_args(
            signal=["sig_base"] * 5 + ["sig_other"] * 5, time_value=date_range("2021-05-01", "2021-05-05").to_list() * 2, value=list(range(10))
        ).api_compatibility_row_df
        expected_df = set_df_dtypes(DataFrame({
            "signal": ["sig_base"] * 5 + ["sig_other"] * 5,
            "geo_type": ["county"] * 10,
            "time_value": map(date_to_time_value, date_range("2021-05-01", "2021-05-5").to_list() * 2),
            "geo_value": ["01234"] * 10,
            "value": range(10),
            "stderr": [10.0] * 10,
            "sample_size": [10.0] * 10,
            "missing_value": [Nans.NOT_MISSING] * 10,
            "missing_stderr": [Nans.NOT_MISSING] * 10,
            "missing_sample_size": [Nans.NOT_MISSING] * 10,
            "issue": map(date_to_time_value, date_range("2021-05-01", "2021-05-5").to_list() * 2),
            "lag": [0] * 10,
        }), CovidcastRows()._DTYPES)
        assert_frame_equal(df, expected_df)
