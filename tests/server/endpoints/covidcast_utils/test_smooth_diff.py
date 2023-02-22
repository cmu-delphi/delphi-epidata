import unittest
from itertools import chain

import pandas as pd

from delphi.epidata.acquisition.covidcast.covidcast_row import CovidcastRows, assert_frame_equal_no_order
from delphi.epidata.server.endpoints.covidcast_utils.smooth_diff import generate_diffed_rows, generate_smoothed_rows
from delphi.epidata.server.endpoints.covidcast_utils.test_utils import diff_df, smooth_df


class TestStreaming(unittest.TestCase):
    def test_generate_smoothed_rows(self):
        data = pd.DataFrame({})
        with self.subTest("an empty dataframe should return an empty dataframe"):
            smoothed_df = CovidcastRows.from_records(generate_smoothed_rows(data.to_dict(orient="records"))).api_row_df
            expected_df = CovidcastRows(rows=[]).api_row_df
            assert_frame_equal_no_order(smoothed_df, expected_df, index=["signal", "geo_value", "time_value"])

        data = CovidcastRows.from_args(time_value=[20210501] * 6, value=[1.0] * 6)
        with self.subTest("a dataframe with not enough entries to make a single smoothed value, should return an empty dataframe"):
            smoothed_df = CovidcastRows.from_records(generate_smoothed_rows(data.as_dicts())).api_row_df
            expected_df = CovidcastRows(rows=[]).api_row_df
            assert_frame_equal_no_order(smoothed_df, expected_df, index=["signal", "geo_value", "time_value"])

        data = CovidcastRows.from_args(time_value=pd.date_range("2021-05-01", "2021-05-13"), value=chain(range(10), [None, 2.0, 1.0]))
        with self.subTest("regular window, nan fill"):
            smoothed_df = CovidcastRows.from_records(generate_smoothed_rows(data.as_dicts())).api_row_df
            expected_df = smooth_df(data.api_row_df, "sig", omit_left_boundary=True)
            assert_frame_equal_no_order(smoothed_df, expected_df, index=["signal", "geo_value", "time_value"])

        with self.subTest("regular window, 0 fill"):
            smoothed_df = CovidcastRows.from_records(generate_smoothed_rows(data.as_dicts(), nan_fill_value=0.0)).api_row_df
            expected_df = smooth_df(data.api_row_df, "sig", nan_fill_value=0.0, omit_left_boundary=True)
            assert_frame_equal_no_order(smoothed_df, expected_df, index=["signal", "geo_value", "time_value"])

        with self.subTest("regular window, different window length"):
            smoothed_df = CovidcastRows.from_records(generate_smoothed_rows(data.as_dicts(), smoother_window_length=8)).api_row_df
            expected_df = smooth_df(data.api_row_df, "sig", window_length=8, omit_left_boundary=True)
            smoothed_df[["time_value", "value"]]
            assert_frame_equal_no_order(smoothed_df, expected_df, index=["signal", "geo_value", "time_value"])

    def test_generate_diffed_rows(self):
        data = CovidcastRows(rows=[])
        with self.subTest("an empty dataframe should return an empty dataframe"):
            diffs_df = CovidcastRows.from_records(generate_diffed_rows(data.as_dicts())).api_row_df
            expected_df = CovidcastRows(rows=[]).api_row_df
            assert_frame_equal_no_order(diffs_df, expected_df, index=["signal", "geo_value", "time_value"])

        data = CovidcastRows.from_args(time_value=[20210501], value=[1.0])
        with self.subTest("a dataframe with not enough data to make one row should return an empty dataframe"):
            diffs_df = CovidcastRows.from_records(generate_diffed_rows(data.as_dicts())).api_row_df
            expected_df = diff_df(data.api_row_df, "sig", omit_left_boundary=True)
            assert_frame_equal_no_order(diffs_df, expected_df, index=["signal", "geo_value", "time_value"])

        data = CovidcastRows.from_args(time_value=pd.date_range("2021-05-01", "2021-05-10"), value=chain(range(7), [None, 2.0, 1.0]))
        with self.subTest("no fill"):
            diffs_df = CovidcastRows.from_records(generate_diffed_rows(data.as_dicts())).api_row_df
            expected_df = diff_df(data.api_row_df, "sig", omit_left_boundary=True)
            assert_frame_equal_no_order(diffs_df, expected_df, index=["signal", "geo_value", "time_value"])

        with self.subTest("yes fill"):
            diffs_df = CovidcastRows.from_records(generate_diffed_rows(data.as_dicts(), nan_fill_value=2.0)).api_row_df
            expected_df = diff_df(data.api_row_df, "sig", nan_fill_value=2.0, omit_left_boundary=True)
            assert_frame_equal_no_order(diffs_df, expected_df, index=["signal", "geo_value", "time_value"])
