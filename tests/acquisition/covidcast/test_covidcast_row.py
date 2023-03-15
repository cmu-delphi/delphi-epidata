import unittest

from pandas import DataFrame
from pandas.testing import assert_frame_equal

from delphi_utils.nancodes import Nans
from delphi.epidata.common.covidcast_row import CovidcastRow, set_df_dtypes
from delphi.epidata.acquisition.covidcast.test_utils import (
    CovidcastTestRow,
    covidcast_rows_as_api_compatibility_row_df, 
    covidcast_rows_as_api_row_df, 
    covidcast_rows_from_args, 
    transpose_dict, 
)

# py3tester coverage target (equivalent to `import *`)
__test_target__ = 'delphi.epidata.acquisition.covidcast.covidcast_row'


class TestCovidcastRows(unittest.TestCase):
    expected_df = set_df_dtypes(DataFrame({
        "source": ["src"] * 10,
        "signal": ["sig_base"] * 5 + ["sig_other"] * 5,
        "time_type": ["day"] * 10,
        "geo_type": ["county"] * 10,
        "time_value": [2021_05_01 + i for i in range(5)] * 2,
        "geo_value": ["01234"] * 10,
        "value": range(10),
        "stderr": [10.0] * 10,
        "sample_size": [10.0] * 10,
        "missing_value": [Nans.NOT_MISSING] * 10,
        "missing_stderr": [Nans.NOT_MISSING] * 10,
        "missing_sample_size": [Nans.NOT_MISSING] * 10,
        "issue": [2021_05_01 + i for i in range(5)] * 2,
        "lag": [0] * 10,
        "direction": [None] * 10
    }), CovidcastRow._pandas_dtypes)

    def test_transpose_dict(self):
        assert transpose_dict(
            {
                "a": [2, 4, 6],
                "b": [3, 5, 7],
                "c": [10, 20, 30]
            }
        ) == [
            {"a": 2, "b": 3, "c": 10}, 
            {"a": 4, "b": 5, "c": 20}, 
            {"a": 6, "b": 7, "c": 30}
        ]


    def test_CovidcastRow(self):
        df = CovidcastTestRow.make_default_row(
            signal="sig_base",
            value=0.0,
            time_value=2021_05_01,
            issue=2021_05_01,
        ).as_api_row_df()
        expected_df = self.expected_df.iloc[0:1]
        assert_frame_equal(df, expected_df)

        df = CovidcastTestRow.make_default_row(
            signal="sig_base",
            value=0.0,
            time_value=2021_05_01,
            issue=2021_05_01,
        ).as_api_compatibility_row_df()
        expected_df = self.expected_df.iloc[0:1][df.columns]
        assert_frame_equal(df, expected_df)


    def test_covidcast_rows(self):
        covidcast_rows = covidcast_rows_from_args(
            signal=["sig_base"] * 5 + ["sig_other"] * 5,
            time_value=[2021_05_01 + i for i in range(5)] * 2,
            value=list(range(10)),
            sanitize_fields = True
        )
        df = covidcast_rows_as_api_row_df(covidcast_rows)
        expected_df = self.expected_df
        assert_frame_equal(df, expected_df)

        covidcast_rows = covidcast_rows_from_args(
            signal=["sig_base"] * 5 + ["sig_other"] * 5,
            time_value=[2021_05_01 + i for i in range(5)] * 2,
            value=list(range(10)),
            sanitize_fields = True
        )
        df = covidcast_rows_as_api_compatibility_row_df(covidcast_rows)
        expected_df = self.expected_df[df.columns]
        assert_frame_equal(df, expected_df)
