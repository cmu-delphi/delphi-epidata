import unittest
from itertools import chain
from unittest.mock import patch
from delphi.epidata.server.utils.dates import iterate_over_range

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from delphi.epidata.acquisition.covidcast.covidcast_row import CovidcastRows, assert_frame_equal_no_order
from delphi.epidata.server._params import SourceSignalPair, TimePair
from delphi.epidata.server.endpoints.covidcast_utils.model import (
    SeriesTransform,
    SourceSignal,
    generate_transformed_rows,
    get_base_signal_transform,
    reindex_iterable,
    get_basename_signals_and_derived_map,
    get_pad_length,
    get_transform_types,
    pad_time_pair,
)
from delphi.epidata.server.endpoints.covidcast_utils.test_utils import DATA_SOURCES_BY_ID, DATA_SIGNALS_BY_KEY, reindex_df, diff_df, smooth_df, diff_smooth_df


@patch("delphi.epidata.server.endpoints.covidcast_utils.model.data_sources_by_id", DATA_SOURCES_BY_ID)
@patch("delphi.epidata.server.endpoints.covidcast_utils.model.data_signals_by_key", DATA_SIGNALS_BY_KEY)
class TestModel(unittest.TestCase):
    def test_reindex_iterable(self):
        with self.subTest(f"Identity operations."):
            assert list(reindex_iterable([])) == []

            data = CovidcastRows.from_args(time_value=pd.date_range("2021-05-03", "2021-05-08").to_list())
            df = CovidcastRows.from_records(reindex_iterable(data.as_dicts())).db_row_df
            assert_frame_equal(df, data.db_row_df)

        with self.subTest("Non-trivial operations"):
            data = CovidcastRows.from_args(time_value=pd.date_range("2021-05-03", "2021-05-08").to_list() + pd.date_range("2021-05-11", "2021-05-14").to_list())
            df = CovidcastRows.from_records(reindex_iterable(data.as_dicts())).db_row_df
            expected_df = reindex_df(data.db_row_df)
            assert_frame_equal_no_order(df, expected_df, index=["source", "signal", "geo_value", "time_value"])

    def test_get_base_signal_transform(self):
        assert get_base_signal_transform(("src", "sig_smooth")) == SeriesTransform.smooth
        assert get_base_signal_transform(("src", "sig_diff_smooth")) == SeriesTransform.diff_smooth
        assert get_base_signal_transform(("src", "sig_diff")) == SeriesTransform.diff
        assert get_base_signal_transform(("src", "sig_diff")) == SeriesTransform.diff
        assert get_base_signal_transform(("src", "sig_base")) == SeriesTransform.identity
        assert get_base_signal_transform(("src", "sig_unknown")) == SeriesTransform.identity

    def test_get_transform_types(self):
        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_diff"])]
        transform_types = get_transform_types(source_signal_pairs)
        expected_transform_types = {SeriesTransform.diff}
        assert transform_types == expected_transform_types

        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_smooth"])]
        transform_types = get_transform_types(source_signal_pairs)
        expected_transform_types = {SeriesTransform.smooth}
        assert transform_types == expected_transform_types

        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_diff_smooth"])]
        transform_types = get_transform_types(source_signal_pairs)
        expected_transform_types = {SeriesTransform.diff_smooth}
        assert transform_types == expected_transform_types

    def test_get_pad_length(self):
        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_diff"])]
        pad_length = get_pad_length(source_signal_pairs, smoother_window_length=7)
        assert pad_length == 1

        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_smooth"])]
        pad_length = get_pad_length(source_signal_pairs, smoother_window_length=5)
        assert pad_length == 4

        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_diff_smooth"])]
        pad_length = get_pad_length(source_signal_pairs, smoother_window_length=10)
        assert pad_length == 10

    def test_pad_time_pair(self):
        # fmt: off
        time_pair = TimePair("day", [20210817, (20210810, 20210815)])
        expected_padded_time_pairs = TimePair("day", [20210817, (20210810, 20210815), (20210803, 20210810)])
        assert pad_time_pair(time_pair, pad_length=7) == expected_padded_time_pairs

        time_pairs = TimePair("day", True)
        expected_padded_time_pairs = TimePair("day", True)
        assert pad_time_pair(time_pairs, pad_length=7) == expected_padded_time_pairs

        time_pair = TimePair("day", [20210817, (20210810, 20210815)])
        expected_padded_time_pairs = TimePair("day", [20210817, (20210810, 20210815), (20210802, 20210810)])
        assert pad_time_pair(time_pair, pad_length=8) == expected_padded_time_pairs

        time_pairs = TimePair("day", [20210817, (20210810, 20210815)])
        assert pad_time_pair(time_pairs, pad_length=0) == time_pairs
        # fmt: on

    def test_generate_transformed_rows(self):
        # fmt: off
        compare_cols = ["signal", "geo_value", "time_value", "time_type", "geo_type", "value", "stderr", "sample_size", "missing_value", "missing_stderr", "missing_sample_size", "direction"]
        with self.subTest("diffed signal test"):
            data = CovidcastRows.from_args(
                signal=["sig_base"] * 5,
                time_value=range(20210501, 20210506),
                value=range(5)
            )
            derived_signals_map = {SourceSignal("src", "sig_base"): [SourceSignal("src", "sig_diff")]}
            df = generate_transformed_rows(data.as_dicts(), derived_signals_map)

            expected_df = diff_df(data.db_row_df, "sig_diff")
            assert_frame_equal_no_order(df[compare_cols], expected_df[compare_cols], index=["signal", "geo_value", "time_value"])

        with self.subTest("smoothed and diffed signals on one base test"):
            data = CovidcastRows.from_args(
                signal=["sig_base"] * 10,
                time_value=pd.date_range("2021-05-01", "2021-05-10"),
                value=range(10),
                stderr=range(10),
                sample_size=range(10)
            )
            derived_signals_map = {SourceSignal("src", "sig_base"): [SourceSignal("src", "sig_diff"), SourceSignal("src", "sig_smooth")]}
            df = generate_transformed_rows(data.as_dicts(), derived_signals_map)

            expected_df = pd.concat([diff_df(data.db_row_df, "sig_diff"), smooth_df(data.db_row_df, "sig_smooth")])
            assert_frame_equal_no_order(df[compare_cols], expected_df[compare_cols], index=["signal", "geo_value", "time_value"])

        with self.subTest("smoothed and diffed signal on two non-continguous regions"):
            data = CovidcastRows.from_args(
                signal=["sig_base"] * 15,
                time_value=chain(pd.date_range("2021-05-01", "2021-05-10"), pd.date_range("2021-05-16", "2021-05-20")),
                value=range(15),
                stderr=range(15),
                sample_size=range(15),
            )
            derived_signals_map = {SourceSignal("src", "sig_base"): [SourceSignal("src", "sig_diff"), SourceSignal("src", "sig_smooth")]}
            df = generate_transformed_rows(data.as_dicts(), derived_signals_map)

            expected_df = pd.concat([diff_df(data.db_row_df, "sig_diff"), smooth_df(data.db_row_df, "sig_smooth")])
            assert_frame_equal_no_order(df[compare_cols], expected_df[compare_cols], index=["signal", "geo_value", "time_value"])

        with self.subTest("diff_smoothed signal on two non-continguous regions"):
            data = CovidcastRows.from_args(
                signal=["sig_base"] * 15,
                time_value=chain(pd.date_range("2021-05-01", "2021-05-10"), pd.date_range("2021-05-16", "2021-05-20")),
                value=range(15),
                stderr=range(15),
                sample_size=range(15),
            )
            derived_signals_map = {SourceSignal("src", "sig_base"): [SourceSignal("src", "sig_diff_smooth")]}
            df = generate_transformed_rows(data.as_dicts(), derived_signals_map)

            expected_df = diff_smooth_df(data.db_row_df, "sig_diff_smooth")
            assert_frame_equal_no_order(df[compare_cols], expected_df[compare_cols], index=["signal", "geo_value", "time_value"])
            # fmt: on

    def test_get_basename_signals(self):
        with self.subTest("none to transform"):
            source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_base"])]
            basename_pairs, _ = get_basename_signals_and_derived_map(source_signal_pairs)
            expected_basename_pairs = [SourceSignalPair(source="src", signal=["sig_base"])]
            assert basename_pairs == expected_basename_pairs

        with self.subTest("unrecognized signal"):
            source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_unknown"])]
            basename_pairs, _ = get_basename_signals_and_derived_map(source_signal_pairs)
            expected_basename_pairs = [SourceSignalPair(source="src", signal=["sig_unknown"])]
            assert basename_pairs == expected_basename_pairs

        with self.subTest("plain"):
            source_signal_pairs = [
                SourceSignalPair(source="src", signal=["sig_diff", "sig_smooth", "sig_diff_smooth", "sig_base"]),
                SourceSignalPair(source="src2", signal=["sig"]),
            ]
            basename_pairs, _ = get_basename_signals_and_derived_map(source_signal_pairs)
            expected_basename_pairs = [
                SourceSignalPair(source="src", signal=["sig_base", "sig_base", "sig_base", "sig_base"]),
                SourceSignalPair(source="src2", signal=["sig"]),
            ]
            assert basename_pairs == expected_basename_pairs

        with self.subTest("test base, diff, smooth"):
            # fmt: off
            data = CovidcastRows.from_args(
                signal=["sig_base"] * 20 + ["sig_other"] * 5,
                time_value=chain(pd.date_range("2021-05-01", "2021-05-10"), pd.date_range("2021-05-21", "2021-05-30"), pd.date_range("2021-05-01", "2021-05-05")),
                value=chain(range(20), range(5)),
                stderr=chain(range(20), range(5)),
                sample_size=chain(range(20), range(5)),
            )
            source_signal_pairs = [SourceSignalPair("src", ["sig_base", "sig_diff", "sig_other", "sig_smooth"])]
            _, derived_signals_map = get_basename_signals_and_derived_map(source_signal_pairs)

            with pytest.raises(ValueError):
                CovidcastRows.from_records(generate_transformed_rows(data.as_dicts(), derived_signals_map)).db_row_df
 
            source_signal_pairs = [SourceSignalPair("src", ["sig_diff", "sig_smooth"])]
            _, derived_signals_map = get_basename_signals_and_derived_map(source_signal_pairs)
            df = generate_transformed_rows(data.as_dicts(), derived_signals_map)

            data_df = data.db_row_df
            expected_df = pd.concat([diff_df(data_df[data_df["signal"] == "sig_base"], "sig_diff"), smooth_df(data_df[data_df["signal"] == "sig_base"], "sig_smooth")])
            compare_cols = ["signal", "geo_value", "time_value", "time_type", "geo_type", "value", "stderr", "sample_size", "missing_value", "missing_stderr", "missing_sample_size", "direction"]
            assert_frame_equal_no_order(df[compare_cols], expected_df[compare_cols], index=["signal", "geo_value", "time_value"])
            # fmt: on

        with self.subTest("test base, diff, smooth; multiple geos"):
            # fmt: off
            data = CovidcastRows.from_args(
                signal=["sig_base"] * 40,
                geo_value=["ak"] * 20 + ["ca"] * 20,
                time_value=chain(pd.date_range("2021-05-01", "2021-05-20"), pd.date_range("2021-05-01", "2021-05-20")),
                value=chain(range(20), range(0, 40, 2)),
                stderr=chain(range(20), range(0, 40, 2)),
                sample_size=chain(range(20), range(0, 40, 2)),
            )
            source_signal_pairs = [SourceSignalPair("src", ["sig_diff", "sig_smooth"])]
            _, derived_signals_map = get_basename_signals_and_derived_map(source_signal_pairs)
            df = generate_transformed_rows(data.as_dicts(), derived_signals_map)

            data_df = data.db_row_df
            expected_df = pd.concat([diff_df(data_df[data_df["signal"] == "sig_base"], "sig_diff"), smooth_df(data_df[data_df["signal"] == "sig_base"], "sig_smooth")])
            compare_cols = ["signal", "geo_value", "time_value", "time_type", "geo_type", "value", "stderr", "sample_size", "missing_value", "missing_stderr", "missing_sample_size", "direction"]
            assert_frame_equal_no_order(df[compare_cols], expected_df[compare_cols], index=["signal", "geo_value", "time_value"])
            # fmt: on

        with self.subTest("empty iterator"):
            source_signal_pairs = [SourceSignalPair("src", ["sig_diff", "sig_smooth"])]
            _, derived_signals_map = get_basename_signals_and_derived_map(source_signal_pairs)
            assert generate_transformed_rows([], derived_signals_map).empty
