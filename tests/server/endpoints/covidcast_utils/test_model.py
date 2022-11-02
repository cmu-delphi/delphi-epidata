import unittest
from itertools import chain
from unittest.mock import patch

import pandas as pd
from more_itertools import interleave_longest, windowed
from pandas.testing import assert_frame_equal

from delphi.epidata.acquisition.covidcast.covidcast_row import CovidcastRows
from delphi.epidata.server._params import SourceSignalPair, TimePair
from delphi.epidata.server.endpoints.covidcast_utils.model import (
    DIFF,
    DIFF_SMOOTH,
    IDENTITY,
    SMOOTH,
    _generate_transformed_rows,
    _get_base_signal_transform,
    _reindex_iterable,
    get_basename_signal_and_jit_generator,
    get_day_range,
    get_pad_length,
    get_transform_types,
    pad_time_pairs,
)
from delphi_utils.nancodes import Nans
from delphi.epidata.server.endpoints.covidcast_utils.test_utils import DATA_SOURCES_BY_ID, DATA_SIGNALS_BY_KEY, _diff_rows, _smooth_rows, _reindex_windowed


@patch("delphi.epidata.server.endpoints.covidcast_utils.model.data_sources_by_id", DATA_SOURCES_BY_ID)
@patch("delphi.epidata.server.endpoints.covidcast_utils.model.data_signals_by_key", DATA_SIGNALS_BY_KEY)
class TestModel(unittest.TestCase):
    def test__reindex_iterable(self):
        # Trivial test.
        time_pairs = [(20210503, 20210508)]
        assert list(_reindex_iterable([], time_pairs)) == []

        data = CovidcastRows.from_args(time_value=pd.date_range("2021-05-03", "2021-05-08").to_list()).api_row_df
        for time_pairs in [[TimePair("day", [(20210503, 20210508)])], [], None]:
            with self.subTest(f"Identity operations: {time_pairs}"):
                df = CovidcastRows.from_records(_reindex_iterable(data.to_dict(orient="records"), time_pairs)).api_row_df
                assert_frame_equal(df, data)

        data = CovidcastRows.from_args(time_value=pd.date_range("2021-05-03", "2021-05-08").to_list() + pd.date_range("2021-05-11", "2021-05-14").to_list()).api_row_df
        with self.subTest("Non-trivial operations"):
            time_pairs = [TimePair("day", [(20210501, 20210513)])]

            df = CovidcastRows.from_records(_reindex_iterable(data.to_dict(orient="records"), time_pairs)).api_row_df
            expected_df = CovidcastRows.from_args(
                time_value=pd.date_range("2021-05-03", "2021-05-13"),
                issue=pd.date_range("2021-05-03", "2021-05-08").to_list() + [None] * 2 + pd.date_range("2021-05-11", "2021-05-13").to_list(),
                lag=[0] * 6 + [None] * 2 + [0] * 3,
                value=chain([10.0] * 6, [None] * 2, [10.0] * 3),
                stderr=chain([10.0] * 6, [None] * 2, [10.0] * 3),
                sample_size=chain([10.0] * 6, [None] * 2, [10.0] * 3),
            ).api_row_df
            assert_frame_equal(df, expected_df)

            df = CovidcastRows.from_records(_reindex_iterable(data.to_dict(orient="records"), time_pairs, fill_value=2.0)).api_row_df
            expected_df = CovidcastRows.from_args(
                time_value=pd.date_range("2021-05-03", "2021-05-13"),
                issue=pd.date_range("2021-05-03", "2021-05-08").to_list() + [None] * 2 + pd.date_range("2021-05-11", "2021-05-13").to_list(),
                lag=[0] * 6 + [None] * 2 + [0] * 3,
                value=chain([10.0] * 6, [2.0] * 2, [10.0] * 3),
                stderr=chain([10.0] * 6, [None] * 2, [10.0] * 3),
                sample_size=chain([10.0] * 6, [None] * 2, [10.0] * 3),
            ).api_row_df
            assert_frame_equal(df, expected_df)

    def test__get_base_signal_transform(self):
        assert _get_base_signal_transform(("src", "sig_smooth")) == SMOOTH
        assert _get_base_signal_transform(("src", "sig_diff_smooth")) == DIFF_SMOOTH
        assert _get_base_signal_transform(("src", "sig_diff")) == DIFF
        assert _get_base_signal_transform(("src", "sig_diff")) == DIFF
        assert _get_base_signal_transform(("src", "sig_base")) == IDENTITY
        assert _get_base_signal_transform(("src", "sig_unknown")) == IDENTITY

    def test_get_transform_types(self):
        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_diff"])]
        transform_types = get_transform_types(source_signal_pairs)
        expected_transform_types = {DIFF}
        assert transform_types == expected_transform_types

        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_smooth"])]
        transform_types = get_transform_types(source_signal_pairs)
        expected_transform_types = {SMOOTH}
        assert transform_types == expected_transform_types

        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_diff_smooth"])]
        transform_types = get_transform_types(source_signal_pairs)
        expected_transform_types = {DIFF_SMOOTH}
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

    def test_pad_time_pairs(self):
        # fmt: off
        time_pairs = [
            TimePair("day", [20210817, (20210810, 20210815)]),
            TimePair("day", True),
            TimePair("day", [20210816])
        ]
        expected_padded_time_pairs = [
            TimePair("day", [20210817, (20210810, 20210815)]), 
            TimePair("day", True), 
            TimePair("day", [20210816]), 
            TimePair("day", [(20210803, 20210810)])
        ]
        assert pad_time_pairs(time_pairs, pad_length=7) == expected_padded_time_pairs

        time_pairs = [
            TimePair("day", [20210817, (20210810, 20210815)]),
            TimePair("day", True),
            TimePair("day", [20210816]),
            TimePair("day", [20210809])
        ]
        expected_padded_time_pairs = [
            TimePair("day", [20210817, (20210810, 20210815)]),
            TimePair("day", True),
            TimePair("day", [20210816]),
            TimePair("day", [20210809]),
            TimePair("day", [(20210801, 20210809)]),
        ]
        assert pad_time_pairs(time_pairs, pad_length=8) == expected_padded_time_pairs

        time_pairs = [
            TimePair("day", [20210817, (20210810, 20210815)])
        ]
        expected_padded_time_pairs = [
            TimePair("day", [20210817, (20210810, 20210815)])
        ]
        assert pad_time_pairs(time_pairs, pad_length=0) == expected_padded_time_pairs
        # fmt: on

    def test__generate_transformed_rows(self):
        # fmt: off
        with self.subTest("diffed signal test"):
            data = CovidcastRows.from_args(
                signal=["sig_base"] * 5,
                time_value=pd.date_range("2021-05-01", "2021-05-05"),
                value=range(5)
            ).api_row_df
            transform_dict = {SourceSignalPair("src", ["sig_base"]): SourceSignalPair("src", ["sig_diff"])}
            df = CovidcastRows.from_records(_generate_transformed_rows(data.to_dict(orient="records"), transform_dict=transform_dict)).api_row_df

            expected_df = CovidcastRows.from_args(
                signal=["sig_diff"] * 4,
                time_value=pd.date_range("2021-05-02", "2021-05-05"),
                value=[1.0] * 4,
                stderr=[None] * 4,
                sample_size=[None] * 4,
                missing_stderr=[Nans.NOT_APPLICABLE] * 4,
                missing_sample_size=[Nans.NOT_APPLICABLE] * 4,
            ).api_row_df

            assert_frame_equal(df, expected_df)

        with self.subTest("smoothed and diffed signals on one base test"):
            data = CovidcastRows.from_args(
                signal=["sig_base"] * 10, 
                time_value=pd.date_range("2021-05-01", "2021-05-10"), 
                value=range(10), 
                stderr=range(10), 
                sample_size=range(10)
            ).api_row_df
            transform_dict = {SourceSignalPair("src", ["sig_base"]): SourceSignalPair("src", ["sig_diff", "sig_smooth"])}
            df = CovidcastRows.from_records(_generate_transformed_rows(data.to_dict(orient="records"), transform_dict=transform_dict)).api_row_df

            expected_df = CovidcastRows.from_args(
                signal=interleave_longest(["sig_diff"] * 9, ["sig_smooth"] * 4),
                time_value=interleave_longest(pd.date_range("2021-05-02", "2021-05-10"), pd.date_range("2021-05-07", "2021-05-10")),
                value=interleave_longest(_diff_rows(data.value.to_list()), _smooth_rows(data.value.to_list())),
                stderr=[None] * 13,
                sample_size=[None] * 13,
            ).api_row_df

            # Test no order.
            idx = ["source", "signal", "time_value"]
            assert_frame_equal(df.set_index(idx).sort_index(), expected_df.set_index(idx).sort_index())
            # Test order.
            assert_frame_equal(df, expected_df)

        with self.subTest("smoothed and diffed signal on two non-continguous regions"):
            data = CovidcastRows.from_args(
                signal=["sig_base"] * 15,
                time_value=chain(pd.date_range("2021-05-01", "2021-05-10"), pd.date_range("2021-05-16", "2021-05-20")),
                value=range(15),
                stderr=range(15),
                sample_size=range(15),
            ).api_row_df
            transform_dict = {SourceSignalPair("src", ["sig_base"]): SourceSignalPair("src", ["sig_diff", "sig_smooth"])}
            time_pairs = [TimePair("day", [(20210501, 20210520)])]
            df = CovidcastRows.from_records(
                _generate_transformed_rows(data.to_dict(orient="records"), time_pairs=time_pairs, transform_dict=transform_dict)
            ).api_row_df

            filled_values = data.value.to_list()[:10] + [None] * 5 + data.value.to_list()[10:]
            filled_time_values = list(chain(pd.date_range("2021-05-01", "2021-05-10"), [None] * 5, pd.date_range("2021-05-16", "2021-05-20")))

            expected_df = CovidcastRows.from_args(
                signal=interleave_longest(["sig_diff"] * 19, ["sig_smooth"] * 14),
                time_value=interleave_longest(pd.date_range("2021-05-02", "2021-05-20"), pd.date_range("2021-05-07", "2021-05-20")),
                value=interleave_longest(_diff_rows(filled_values), _smooth_rows(filled_values)),
                stderr=[None] * 33,
                sample_size=[None] * 33,
                issue=interleave_longest(_reindex_windowed(filled_time_values, 2), _reindex_windowed(filled_time_values, 7)),
            ).api_row_df
            # Test no order.
            idx = ["source", "signal", "time_value"]
            assert_frame_equal(df.set_index(idx).sort_index(), expected_df.set_index(idx).sort_index())
            # Test order.
            assert_frame_equal(df, expected_df)
        # fmt: on

    def test_get_basename_signals(self):
        with self.subTest("none to transform"):
            source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_base"])]
            basename_pairs, _ = get_basename_signal_and_jit_generator(source_signal_pairs)
            expected_basename_pairs = [SourceSignalPair(source="src", signal=["sig_base"])]
            assert basename_pairs == expected_basename_pairs

        with self.subTest("unrecognized signal"):
            source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_unknown"])]
            basename_pairs, _ = get_basename_signal_and_jit_generator(source_signal_pairs)
            expected_basename_pairs = [SourceSignalPair(source="src", signal=["sig_unknown"])]
            assert basename_pairs == expected_basename_pairs

        with self.subTest("plain"):
            source_signal_pairs = [
                SourceSignalPair(source="src", signal=["sig_diff", "sig_smooth", "sig_diff_smooth", "sig_base"]),
                SourceSignalPair(source="src2", signal=["sig"]),
            ]
            basename_pairs, _ = get_basename_signal_and_jit_generator(source_signal_pairs)
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
            ).api_row_df
            source_signal_pairs = [SourceSignalPair("src", ["sig_base", "sig_diff", "sig_other", "sig_smooth"])]
            _, row_transform_generator = get_basename_signal_and_jit_generator(source_signal_pairs)
            time_pairs = [TimePair("day", [(20210501, 20210530)])]
            df = CovidcastRows.from_records(row_transform_generator(data.to_dict(orient="records"), time_pairs=time_pairs)).api_row_df

            filled_values = list(chain(range(10), [None] * 10, range(10, 20)))
            filled_time_values = list(chain(pd.date_range("2021-05-01", "2021-05-10"), [None] * 10, pd.date_range("2021-05-21", "2021-05-30")))

            expected_df = CovidcastRows.from_args(
                signal=["sig_base"] * 30 + ["sig_diff"] * 29 + ["sig_other"] * 5 + ["sig_smooth"] * 24,
                time_value=chain(
                    pd.date_range("2021-05-01", "2021-05-30"),
                    pd.date_range("2021-05-02", "2021-05-30"),
                    pd.date_range("2021-05-01", "2021-05-05"),
                    pd.date_range("2021-05-07", "2021-05-30")
                ),
                value=chain(
                    filled_values, 
                    _diff_rows(filled_values), 
                    range(5), 
                    _smooth_rows(filled_values)
                ),
                stderr=chain(
                    chain(range(10), [None] * 10, range(10, 20)),
                    chain([None] * 29),
                    range(5),
                    chain([None] * 24),
                ),
                sample_size=chain(
                    chain(range(10), [None] * 10, range(10, 20)),
                    chain([None] * 29),
                    range(5),
                    chain([None] * 24),
                ),
                issue=chain(filled_time_values, _reindex_windowed(filled_time_values, 2), pd.date_range("2021-05-01", "2021-05-05"), _reindex_windowed(filled_time_values, 7)),
            ).api_row_df
            # fmt: on
            # Test no order.
            idx = ["source", "signal", "time_value"]
            assert_frame_equal(df.set_index(idx).sort_index(), expected_df.set_index(idx).sort_index())

        with self.subTest("test base, diff, smooth; multiple geos"):
            # fmt: off
            data = CovidcastRows.from_args(
                signal=["sig_base"] * 40,
                geo_value=["ak"] * 20 + ["ca"] * 20,
                time_value=chain(pd.date_range("2021-05-01", "2021-05-20"), pd.date_range("2021-05-01", "2021-05-20")),
                value=chain(range(20), range(0, 40, 2)),
                stderr=chain(range(20), range(0, 40, 2)),
                sample_size=chain(range(20), range(0, 40, 2)),
            ).api_row_df
            source_signal_pairs = [SourceSignalPair("src", ["sig_base", "sig_diff", "sig_other", "sig_smooth"])]
            _, row_transform_generator = get_basename_signal_and_jit_generator(source_signal_pairs)
            df = CovidcastRows.from_records(row_transform_generator(data.to_dict(orient="records"))).api_row_df

            expected_df = CovidcastRows.from_args(
                signal=["sig_base"] * 40 + ["sig_diff"] * 38 + ["sig_smooth"] * 28,
                geo_value=["ak"] * 20 + ["ca"] * 20 + ["ak"] * 19 + ["ca"] * 19 + ["ak"] * 14 + ["ca"] * 14,
                time_value=chain(
                    pd.date_range("2021-05-01", "2021-05-20"),
                    pd.date_range("2021-05-01", "2021-05-20"),
                    pd.date_range("2021-05-02", "2021-05-20"),
                    pd.date_range("2021-05-02", "2021-05-20"),
                    pd.date_range("2021-05-07", "2021-05-20"),
                    pd.date_range("2021-05-07", "2021-05-20"),
                ),
                value=chain(
                    chain(range(20), range(0, 40, 2)), 
                    chain([1] * 19, [2] * 19), 
                    chain([sum(x) / len(x) for x in windowed(range(20), 7)], 
                    [sum(x) / len(x) for x in windowed(range(0, 40, 2), 7)])
                ),
                stderr=chain(
                    chain(range(20), range(0, 40, 2)),
                    chain([None] * 38),
                    chain([None] * 28),
                ),
                sample_size=chain(
                    chain(range(20), range(0, 40, 2)),
                    chain([None] * 38),
                    chain([None] * 28),
                ),
            ).api_row_df
            # fmt: on
            # Test no order.
            idx = ["source", "signal", "time_value"]
            assert_frame_equal(df.set_index(idx).sort_index(), expected_df.set_index(idx).sort_index())

        with self.subTest("empty iterator"):
            source_signal_pairs = [SourceSignalPair("src", ["sig_base", "sig_diff", "sig_smooth"])]
            _, row_transform_generator = get_basename_signal_and_jit_generator(source_signal_pairs)
            assert list(row_transform_generator({})) == []

    def test_get_day_range(self):
        assert list(get_day_range([TimePair("day", [20210817])])) == [20210817]
        assert list(get_day_range([TimePair("day", [20210817, (20210810, 20210815)])])) == [20210810, 20210811, 20210812, 20210813, 20210814, 20210815, 20210817]
        assert list(get_day_range([TimePair("day", [(20210801, 20210805)]), TimePair("day", [(20210803, 20210807)])])) == [20210801, 20210802, 20210803, 20210804, 20210805, 20210806, 20210807]
