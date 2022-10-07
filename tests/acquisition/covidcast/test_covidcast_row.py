import unittest

from pandas import DataFrame, date_range
from pandas.testing import assert_frame_equal

from delphi_utils.nancodes import Nans
from delphi.epidata.server.utils.dates import day_to_time_value
from delphi.epidata.acquisition.covidcast.covidcast_row import (
    covidcast_rows_as_api_compatibility_row_df, 
    covidcast_rows_as_api_row_df, 
    covidcast_rows_from_args, 
    set_df_dtypes, 
    transpose_dict, 
    CovidcastRow
)

# py3tester coverage target (equivalent to `import *`)
__test_target__ = 'delphi.epidata.acquisition.covidcast.covidcast_row'


class TestCovidcastRows(unittest.TestCase):
    def test_transpose_dict(self):
        assert transpose_dict(dict([["a", [2, 4, 6]], ["b", [3, 5, 7]], ["c", [10, 20, 30]]])) == [{"a": 2, "b": 3, "c": 10}, {"a": 4, "b": 5, "c": 20}, {"a": 6, "b": 7, "c": 30}]


    def test_CovidcastRow(self):
        df = CovidcastRow.make_default_row(value=5.0).api_row_df
        expected_df = set_df_dtypes(DataFrame.from_records([{
            "source": "src",
            "signal": "sig",
            "time_type": "day",
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
            "direction": None
        }]), dtypes = CovidcastRow._pandas_dtypes)
        assert_frame_equal(df, expected_df)

        df = CovidcastRow.make_default_row(value=5.0).api_compatibility_row_df
        expected_df = set_df_dtypes(DataFrame.from_records([{
            "signal": "sig",
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
            "direction": None
        }]), dtypes = CovidcastRow._pandas_dtypes)
        assert_frame_equal(df, expected_df)


    def test_covidcast_rows(self):
        covidcast_rows = covidcast_rows_from_args(signal=["sig_base"] * 5 + ["sig_other"] * 5, time_value=date_range("2021-05-01", "2021-05-05").to_list() * 2, value=list(range(10)))
        df = covidcast_rows_as_api_row_df(covidcast_rows)
        expected_df = set_df_dtypes(DataFrame({
            "source": ["src"] * 10,
            "signal": ["sig_base"] * 5 + ["sig_other"] * 5,
            "time_type": ["day"] * 10,
            "geo_type": ["county"] * 10,
            "time_value": map(day_to_time_value, date_range("2021-05-01", "2021-05-5").to_list() * 2),
            "geo_value": ["01234"] * 10,
            "value": range(10),
            "stderr": [10.0] * 10,
            "sample_size": [10.0] * 10,
            "missing_value": [Nans.NOT_MISSING] * 10,
            "missing_stderr": [Nans.NOT_MISSING] * 10,
            "missing_sample_size": [Nans.NOT_MISSING] * 10,
            "issue": map(day_to_time_value, date_range("2021-05-01", "2021-05-5").to_list() * 2),
            "lag": [0] * 10,
            "direction": [None] * 10
        }), CovidcastRow._pandas_dtypes)
        assert_frame_equal(df, expected_df)

        covidcast_rows = covidcast_rows_from_args(signal=["sig_base"] * 5 + ["sig_other"] * 5, time_value=date_range("2021-05-01", "2021-05-05").to_list() * 2, value=list(range(10)))
        df = covidcast_rows_as_api_compatibility_row_df(covidcast_rows)
        expected_df = set_df_dtypes(DataFrame({
            "signal": ["sig_base"] * 5 + ["sig_other"] * 5,
            "time_value": map(day_to_time_value, date_range("2021-05-01", "2021-05-5").to_list() * 2),
            "geo_value": ["01234"] * 10,
            "value": range(10),
            "stderr": [10.0] * 10,
            "sample_size": [10.0] * 10,
            "missing_value": [Nans.NOT_MISSING] * 10,
            "missing_stderr": [Nans.NOT_MISSING] * 10,
            "missing_sample_size": [Nans.NOT_MISSING] * 10,
            "issue": map(day_to_time_value, date_range("2021-05-01", "2021-05-5").to_list() * 2),
            "lag": [0] * 10,
            "direction": [None] * 10
        }), CovidcastRow._pandas_dtypes)
        assert_frame_equal(df, expected_df)
