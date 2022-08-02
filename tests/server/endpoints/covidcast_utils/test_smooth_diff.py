from pandas import DataFrame, date_range
from pandas.testing import assert_frame_equal
from numpy import nan, isnan
from itertools import chain
from pytest import raises
import unittest

from .....src.acquisition.covidcast.covidcast_row import CovidcastRows
from .....src.server.endpoints.covidcast_utils.smooth_diff import generate_diffed_rows, generate_smoothed_rows, _smoother
from .test_model import _diff_rows, _smooth_rows, _reindex_windowed


class TestStreaming(unittest.TestCase):
    def test__smoother(self):
        assert _smoother(list(range(1, 7)), [1] * 6) == sum(range(1, 7))
        assert _smoother([1] * 6, list(range(1, 7))) == sum(range(1, 7))
        assert isnan(_smoother([1, nan, nan]))
        with raises(TypeError, match=r"unsupported operand type*"):
            _smoother([1, nan, None])


    def test_generate_smoothed_rows(self):
        with self.subTest("an empty dataframe should return an empty dataframe"):
            data = DataFrame({})
            smoothed_df = CovidcastRows.from_records(generate_smoothed_rows(data.to_dict(orient='records'))).api_row_df
            expected_df = CovidcastRows(rows=[]).api_row_df
            assert_frame_equal(smoothed_df, expected_df)

        with self.subTest("a dataframe with not enough entries to make a single smoothed value, should return an empty dataframe"):
            data = CovidcastRows.from_args(
                time_value=[20210501] * 6,
                value=[1.0] * 6
            ).api_row_df

            smoothed_df = CovidcastRows.from_records(generate_smoothed_rows(data.to_dict(orient='records'))).api_row_df
            expected_df = CovidcastRows(rows=[]).api_row_df
            assert_frame_equal(smoothed_df, expected_df)

        data = CovidcastRows.from_args(
            time_value=date_range("2021-05-01", "2021-05-13"),
            value=list(chain(range(10), [None, 2., 1.]))
        ).api_row_df

        with self.subTest("regular window, nan fill"):
            smoothed_df = CovidcastRows.from_records(generate_smoothed_rows(data.to_dict(orient='records'))).api_row_df

            smoothed_values = _smooth_rows(data.value.to_list())
            reduced_time_values = data.time_value.to_list()[-len(smoothed_values):]

            expected_df = CovidcastRows.from_args(
                time_value=reduced_time_values,
                value=smoothed_values,
                stderr=[None] * len(smoothed_values),
                sample_size=[None] * len(smoothed_values),
            ).api_row_df

            assert_frame_equal(smoothed_df, expected_df)

        with self.subTest("regular window, 0 fill"):
            smoothed_df = CovidcastRows.from_records(generate_smoothed_rows(data.to_dict(orient='records'), nan_fill_value=0.)).api_row_df
    
            smoothed_values = _smooth_rows([v if v is not None and not isnan(v) else 0. for v in data.value.to_list()])
            reduced_time_values = data.time_value.to_list()[-len(smoothed_values):]

            expected_df = CovidcastRows.from_args(
                time_value=reduced_time_values,
                value=smoothed_values,
                stderr=[None] * len(smoothed_values),
                sample_size=[None] * len(smoothed_values),
            ).api_row_df

            assert_frame_equal(smoothed_df, expected_df)

        with self.subTest("regular window, different window length"):
            smoothed_df = CovidcastRows.from_records(generate_smoothed_rows(data.to_dict(orient='records'), smoother_window_length=8)).api_row_df

            smoothed_values = _smooth_rows(data.value.to_list(), window_length=8)
            reduced_time_values = data.time_value.to_list()[-len(smoothed_values):]

            expected_df = CovidcastRows.from_args(
                time_value=reduced_time_values,
                value=smoothed_values,
                stderr=[None] * len(smoothed_values),
                sample_size=[None] * len(smoothed_values),
            ).api_row_df
            assert_frame_equal(smoothed_df, expected_df)

        with self.subTest("regular window, different kernel"):
            smoothed_df = CovidcastRows.from_records(generate_smoothed_rows(data.to_dict(orient='records'), smoother_kernel=list(range(8)))).api_row_df

            smoothed_values = _smooth_rows(data.value.to_list(), kernel=list(range(8)))
            reduced_time_values = data.time_value.to_list()[-len(smoothed_values):]

            expected_df = CovidcastRows.from_args(
                time_value=reduced_time_values,
                value=smoothed_values,
                stderr=[None] * len(smoothed_values),
                sample_size=[None] * len(smoothed_values),
            ).api_row_df
            assert_frame_equal(smoothed_df, expected_df)

        with self.subTest("conflicting smoother args validation, smoother kernel should overwrite window length"):
            smoothed_df = CovidcastRows.from_records(generate_smoothed_rows(data.to_dict(orient='records'), smoother_kernel=[1/7.]*7, smoother_window_length=10)).api_row_df

            smoothed_values = _smooth_rows(data.value.to_list(), kernel=[1/7.]*7)
            reduced_time_values = data.time_value.to_list()[-len(smoothed_values):]

            expected_df = CovidcastRows.from_args(
                time_value=reduced_time_values,
                value=smoothed_values,
                stderr=[None] * len(smoothed_values),
                sample_size=[None] * len(smoothed_values),
            ).api_row_df
            assert_frame_equal(smoothed_df, expected_df)


    def test_generate_diffed_rows(self):
        with self.subTest("an empty dataframe should return an empty dataframe"):
            data = DataFrame({})
            diffs_df = CovidcastRows.from_records(generate_diffed_rows(data.to_dict(orient='records'))).api_row_df
            expected_df = CovidcastRows(rows=[]).api_row_df
            assert_frame_equal(diffs_df, expected_df)

        with self.subTest("a dataframe with not enough data to make one row should return an empty dataframe"):
            data = CovidcastRows.from_args(time_value=[20210501], value=[1.0]).api_row_df
            diffs_df = CovidcastRows.from_records(generate_diffed_rows(data.to_dict(orient='records'))).api_row_df
            expected_df = CovidcastRows(rows=[]).api_row_df
            assert_frame_equal(diffs_df, expected_df)

        data = CovidcastRows.from_args(
            time_value=date_range("2021-05-01", "2021-05-10"),
            value=chain(range(7), [None, 2., 1.])
        ).api_row_df

        with self.subTest("no fill"):
            diffs_df = CovidcastRows.from_records(generate_diffed_rows(data.to_dict(orient='records'))).api_row_df

            diffed_values = _diff_rows(data.value.to_list())
            reduced_time_values = data.time_value.to_list()[-len(diffed_values):]

            expected_df = CovidcastRows.from_args(
                time_value=reduced_time_values,
                value=diffed_values,
                stderr=[None] * len(diffed_values),
                sample_size=[None] * len(diffed_values),
            ).api_row_df

            assert_frame_equal(diffs_df, expected_df)

        with self.subTest("yes fill"):
            diffs_df = CovidcastRows.from_records(generate_diffed_rows(data.to_dict(orient='records'), nan_fill_value=2.)).api_row_df

            diffed_values = _diff_rows([v if v is not None and not isnan(v) else 2. for v in data.value.to_list()])
            reduced_time_values = data.time_value.to_list()[-len(diffed_values):]

            expected_df = CovidcastRows.from_args(
                time_value=reduced_time_values,
                value=diffed_values,
                stderr=[None] * len(diffed_values),
                sample_size=[None] * len(diffed_values),
            ).api_row_df

            assert_frame_equal(diffs_df, expected_df)
