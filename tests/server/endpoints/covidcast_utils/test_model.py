from typing import Sequence
import unittest
from itertools import chain
from more_itertools import interleave_longest, windowed
from pandas import DataFrame, date_range
from pandas.testing import assert_frame_equal

from delphi_utils.nancodes import Nans

from delphi.epidata.server.utils import CovidcastRecords
from delphi.epidata.server._params import SourceSignalPair, TimePair
from delphi.epidata.server.endpoints.covidcast_utils.model import (
    IDENTITY,
    DIFF,
    SMOOTH,
    DIFF_SMOOTH,
    DataSource,
    DataSignal,
    _resolve_all_signals,
    _reindex_iterable,
    _get_base_signal_transform,
    get_transform_types,
    get_pad_length,
    pad_time_pairs,
    get_day_range,
    _generate_transformed_rows,
    get_basename_signals,
)

DATA_SIGNALS_BY_KEY = {
    ("src", "sig_diff"): DataSignal(
        source="src",
        signal="sig_diff",
        signal_basename="sig_base",
        name="src",
        active=True,
        short_description="",
        description="",
        time_label="",
        value_label="",
        is_cumulative=False,
        compute_from_base=True,
    ),
    ("src", "sig_smooth"): DataSignal(
        source="src",
        signal="sig_smooth",
        signal_basename="sig_base",
        name="src",
        active=True,
        short_description="",
        description="",
        time_label="",
        value_label="",
        is_cumulative=True,
        is_smoothed=True,
        compute_from_base=True,
    ),
    ("src", "sig_diff_smooth"): DataSignal(
        source="src",
        signal="sig_diff_smooth",
        signal_basename="sig_base",
        name="src",
        active=True,
        short_description="",
        description="",
        time_label="",
        value_label="",
        is_cumulative=False,
        is_smoothed=True,
        compute_from_base=True,
    ),
    ("src", "sig_base"): DataSignal(
        source="src", signal="sig_base", signal_basename="sig_base", name="src", active=True, short_description="", description="", time_label="", value_label="", is_cumulative=True,
    ),
    ("src2", "sig_base"): DataSignal(
        source="src2", signal="sig_base", signal_basename="sig_base", name="sig_base", active=True, short_description="", description="", time_label="", value_label="", is_cumulative=True,
    ),
    ("src2", "sig_diff_smooth"): DataSignal(
        source="src2",
        signal="sig_diff_smooth",
        signal_basename="sig_base",
        name="sig_smooth",
        active=True,
        short_description="",
        description="",
        time_label="",
        value_label="",
        is_cumulative=False,
        is_smoothed=True,
        compute_from_base=True,
    ),
}

DATA_SOURCES_BY_ID = {
    "src": DataSource(
        source="src",
        db_source="src",
        name="src",
        description="",
        reference_signal="sig_base",
        signals=[DATA_SIGNALS_BY_KEY[key] for key in DATA_SIGNALS_BY_KEY if key[0] == "src"],
    ),
    "src2": DataSource(
        source="src2",
        db_source="src2",
        name="src2",
        description="",
        reference_signal="sig_base",
        signals=[DATA_SIGNALS_BY_KEY[key] for key in DATA_SIGNALS_BY_KEY if key[0] == "src2"],
    ),
}


class TestModel(unittest.TestCase):
    def test__resolve_all_signals(self):
        source_signal_pair = [SourceSignalPair(source="src", signal=True), SourceSignalPair(source="src", signal=["sig_unknown"])]
        resolved_source_signal_pair = _resolve_all_signals(source_signal_pair, DATA_SOURCES_BY_ID)
        expected_source_signal_pair = [
            SourceSignalPair(source="src", signal=["sig_diff", "sig_smooth", "sig_diff_smooth", "sig_base"]),
            SourceSignalPair(source="src", signal=["sig_unknown"]),
        ]
        assert resolved_source_signal_pair == expected_source_signal_pair

    def test__reindex_iterable(self):
        data = CovidcastRecords(time_values=date_range("2021-05-03", "2021-05-08").to_list()).as_dataframe()
        day_range = get_day_range(TimePair("day", [(20210503, 20210508)]))
        df = DataFrame.from_records(_reindex_iterable(data.to_dict(orient='records'), day_range))
        assert_frame_equal(df, data)

        data = CovidcastRecords(time_values=date_range("2021-05-03", "2021-05-08").to_list() + date_range("2021-05-11", "2021-05-14").to_list()).as_dataframe()
        day_range = get_day_range(TimePair("day", [(20210501, 20210513)]))
        df = DataFrame.from_records(_reindex_iterable(data.to_dict(orient='records'), day_range))
        expected_df = CovidcastRecords(
            time_values=date_range("2021-05-01", "2021-05-13"),
            values=chain([None] * 2, [1.] * 6, [None] * 2, [1.] * 3),
            stderrs=chain([None] * 2, [1.] * 6, [None] * 2, [1.] * 3),
            sample_sizes=chain([None] * 2, [1.] * 6, [None] * 2, [1.] * 3)
        ).as_dataframe()
        assert_frame_equal(df, expected_df)

        df = DataFrame.from_records(_reindex_iterable(data.to_dict(orient='records'), day_range, fill_value=2.))
        expected_df = CovidcastRecords(
            time_values=date_range("2021-05-01", "2021-05-13"),
            values=chain([2.] * 2, [1.] * 6, [2.] * 2, [1.] * 3),
            stderrs=chain([None] * 2, [1.] * 6, [None] * 2, [1.] * 3),
            sample_sizes=chain([None] * 2, [1.] * 6, [None] * 2, [1.] * 3),
        ).as_dataframe()
        assert_frame_equal(df, expected_df)

    def test__get_base_signal_transform(self):
        assert _get_base_signal_transform(DATA_SIGNALS_BY_KEY[("src", "sig_smooth")], DATA_SIGNALS_BY_KEY) == SMOOTH
        assert _get_base_signal_transform(DATA_SIGNALS_BY_KEY[("src", "sig_diff_smooth")], DATA_SIGNALS_BY_KEY) == DIFF_SMOOTH
        assert _get_base_signal_transform(DATA_SIGNALS_BY_KEY[("src", "sig_diff")], DATA_SIGNALS_BY_KEY) == DIFF
        assert _get_base_signal_transform(("src", "sig_diff"), DATA_SIGNALS_BY_KEY) == DIFF
        assert _get_base_signal_transform(DATA_SIGNALS_BY_KEY[("src", "sig_base")], DATA_SIGNALS_BY_KEY) == IDENTITY
        assert _get_base_signal_transform(("src", "sig_unknown"), DATA_SIGNALS_BY_KEY) == IDENTITY

    def test_get_transform_types(self):
        source_signal_pairs = [SourceSignalPair(source="src", signal=True)]
        transform_types = get_transform_types(source_signal_pairs, data_sources_by_id=DATA_SOURCES_BY_ID, data_signals_by_key=DATA_SIGNALS_BY_KEY)
        expected_transform_types = {IDENTITY, DIFF, SMOOTH, DIFF_SMOOTH}
        assert transform_types == expected_transform_types
        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_diff"])]
        transform_types = get_transform_types(source_signal_pairs, data_sources_by_id=DATA_SOURCES_BY_ID, data_signals_by_key=DATA_SIGNALS_BY_KEY)
        expected_transform_types = {DIFF}
        assert transform_types == expected_transform_types
        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_smooth"])]
        transform_types = get_transform_types(source_signal_pairs, data_sources_by_id=DATA_SOURCES_BY_ID, data_signals_by_key=DATA_SIGNALS_BY_KEY)
        expected_transform_types = {SMOOTH}
        assert transform_types == expected_transform_types
        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_diff_smooth"])]
        transform_types = get_transform_types(source_signal_pairs, data_sources_by_id=DATA_SOURCES_BY_ID, data_signals_by_key=DATA_SIGNALS_BY_KEY)
        expected_transform_types = {DIFF_SMOOTH}
        assert transform_types == expected_transform_types

    def test_get_pad_length(self):
        source_signal_pairs = [SourceSignalPair(source="src", signal=True)]
        pad_length = get_pad_length(source_signal_pairs, smoother_window_length=7, data_sources_by_id=DATA_SOURCES_BY_ID, data_signals_by_key=DATA_SIGNALS_BY_KEY)
        assert pad_length == 7
        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_diff"])]
        pad_length = get_pad_length(source_signal_pairs, smoother_window_length=7, data_sources_by_id=DATA_SOURCES_BY_ID, data_signals_by_key=DATA_SIGNALS_BY_KEY)
        assert pad_length == 1
        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_smooth"])]
        pad_length = get_pad_length(source_signal_pairs, smoother_window_length=5, data_sources_by_id=DATA_SOURCES_BY_ID, data_signals_by_key=DATA_SIGNALS_BY_KEY)
        assert pad_length == 4
        source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_diff_smooth"])]
        pad_length = get_pad_length(source_signal_pairs, smoother_window_length=10, data_sources_by_id=DATA_SOURCES_BY_ID, data_signals_by_key=DATA_SIGNALS_BY_KEY)
        assert pad_length == 10

    def test_pad_time_pairs(self):
        time_pairs = [TimePair("day", [20210817, (20210810, 20210815)]), TimePair("day", True), TimePair("day", [20210816])]
        padded_time_pairs = pad_time_pairs(time_pairs, pad_length=7)
        expected_padded_time_pairs = [TimePair("day", [20210817, (20210810, 20210815)]), TimePair("day", True), TimePair("day", [20210816]), TimePair("day", [(20210803, 20210810)])]
        assert padded_time_pairs == expected_padded_time_pairs
        time_pairs = [TimePair("day", [20210817, (20210810, 20210815)]), TimePair("day", True), TimePair("day", [20210816]), TimePair("day", [20210809])]
        padded_time_pairs = pad_time_pairs(time_pairs, pad_length=8)
        expected_padded_time_pairs = [TimePair("day", [20210817, (20210810, 20210815)]), TimePair("day", True), TimePair("day", [20210816]), TimePair("day", [20210809]), TimePair("day", [(20210801, 20210809)])]
        assert padded_time_pairs == expected_padded_time_pairs
        time_pairs = [TimePair("day", [20210817, (20210810, 20210815)])]
        padded_time_pairs = pad_time_pairs(time_pairs, pad_length=0)
        expected_padded_time_pairs = [TimePair("day", [20210817, (20210810, 20210815)])]
        assert padded_time_pairs == expected_padded_time_pairs

    def test_get_day_range(self):
        time_pair = TimePair("day", [20210817, (20210810, 20210815)])
        day_range = get_day_range(time_pair)
        expected_day_range = TimePair("day", [20210810, 20210811, 20210812, 20210813, 20210814, 20210815, 20210817])
        assert day_range == expected_day_range
        time_pairs = [TimePair("day", [20210817])]
        day_range = get_day_range(time_pairs)
        expected_day_range = TimePair("day", [20210817])
        assert day_range == expected_day_range
        time_pairs = [TimePair("day", [(20210801, 20210805)]), TimePair("day", [(20210803, 20210807)])]
        day_range = get_day_range(time_pairs)
        expected_day_range = TimePair("day", [20210801, 20210802, 20210803, 20210804, 20210805, 20210806, 20210807])
        assert day_range == expected_day_range

    def _diff_rows(self, rows: Sequence[float]):
        return [float(x - y) if x is not None and y is not None else None for x, y in zip(rows[1:], rows[:-1])]

    def _smooth_rows(self, rows: Sequence[float]):
        return [sum(e)/len(e) if None not in e else None for e in windowed(rows, 7)]

    def _find_missing(self, rows: Sequence[float]):
        return [Nans.NOT_APPLICABLE if row is None else Nans.NOT_MISSING for row in rows]

    def test__generate_transformed_rows(self):
        with self.subTest("diffed signal test"):
            data = CovidcastRecords(signals=["sig_base"] * 5, time_values=date_range("2021-05-01", "2021-05-05"), values=range(5)).as_dataframe()
            transform_dict = {("src", "sig_base"): [("src", "sig_diff")]}
            df = DataFrame.from_records(
                _generate_transformed_rows(data.to_dict(orient="records"), transform_dict=transform_dict, data_signals_by_key=DATA_SIGNALS_BY_KEY)
            )
            expected_df = CovidcastRecords(
                signals=["sig_diff"] * 4, time_values=date_range("2021-05-02", "2021-05-05"), values=[1.0] * 4, stderrs=[None] * 4, sample_sizes=[None] * 4, missing_stderrs=[Nans.NOT_APPLICABLE] * 4, missing_sample_sizes=[Nans.NOT_APPLICABLE] * 4,
            ).as_dataframe()
            assert_frame_equal(df, expected_df)

        with self.subTest("smoothed and diffed signals on one base test"):
            data = CovidcastRecords(
                signals=["sig_base"] * 10, time_values=date_range("2021-05-01", "2021-05-10"), values=range(10), stderrs=range(10), sample_sizes=range(10)
            ).as_dataframe()
            values = list(range(10))
            transform_dict = {("src", "sig_base"): [("src", "sig_diff"), ("src", "sig_smooth")]}
            df = DataFrame.from_records(_generate_transformed_rows(data.to_dict(orient="records"), transform_dict=transform_dict, data_signals_by_key=DATA_SIGNALS_BY_KEY))
            expected_df = CovidcastRecords(
                signals=interleave_longest(["sig_diff"] * 9, ["sig_smooth"] * 4),
                time_values=interleave_longest(date_range("2021-05-02", "2021-05-10"), date_range("2021-05-07", "2021-05-10")),
                values=interleave_longest(self._diff_rows(values), self._smooth_rows(values)),
                stderrs=[None] * 13,
                sample_sizes=[None] * 13,
            ).as_dataframe()
            assert_frame_equal(df, expected_df)
            idx = ["source", "signal", "time_value"]
            assert_frame_equal(df.set_index(idx).sort_index(), expected_df.set_index(idx).sort_index())

        with self.subTest("smoothed and diffed signal on two non-continguous regions"):
            data = CovidcastRecords(
                signals=["sig_base"] * 15, time_values=chain(date_range("2021-05-01", "2021-05-10"), date_range("2021-05-16", "2021-05-20")), values=range(15), stderrs=range(15), sample_sizes=range(15)
            ).as_dataframe()
            values = list(chain(range(10), [None] * 5, range(10, 15)))
            transform_dict = {("src", "sig_base"): [("src", "sig_diff"), ("src", "sig_smooth")]}
            time_pairs = TimePair("day", [(20210501, 20210520)])
            df = DataFrame.from_records(_generate_transformed_rows(data.to_dict(orient="records"), time_pairs=time_pairs, transform_dict=transform_dict, data_signals_by_key=DATA_SIGNALS_BY_KEY))
            expected_df = CovidcastRecords(
                signals=interleave_longest(["sig_diff"] * 19, ["sig_smooth"] * 14),
                time_values=interleave_longest(date_range("2021-05-02", "2021-05-20"), date_range("2021-05-07", "2021-05-20")),
                values=interleave_longest(self._diff_rows(values), self._smooth_rows(values)),
                stderrs=[None] * 33,
                sample_sizes=[None] * 33,
            ).as_dataframe()
            assert_frame_equal(df, expected_df)
            idx = ["source", "signal", "time_value"]
            assert_frame_equal(df.set_index(idx).sort_index(), expected_df.set_index(idx).sort_index())

    def test_get_basename_signals(self):
        with self.subTest("none to transform"):
            source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_base"])]
            basename_pairs, _ = get_basename_signals(source_signal_pairs, DATA_SOURCES_BY_ID, DATA_SIGNALS_BY_KEY)
            expected_basename_pairs = [SourceSignalPair(source="src", signal=["sig_base"])]
            assert basename_pairs == expected_basename_pairs

        with self.subTest("unrecognized signal"):
            source_signal_pairs = [SourceSignalPair(source="src", signal=["sig_unknown"])]
            basename_pairs, _ = get_basename_signals(source_signal_pairs, DATA_SOURCES_BY_ID, DATA_SIGNALS_BY_KEY)
            expected_basename_pairs = [SourceSignalPair(source="src", signal=["sig_unknown"])]
            assert basename_pairs == expected_basename_pairs

        with self.subTest("plain"):
            source_signal_pairs = [
                SourceSignalPair(source="src", signal=["sig_diff", "sig_smooth", "sig_diff_smooth", "sig_base"]),
                SourceSignalPair(source="src2", signal=["sig"]),
            ]
            basename_pairs, _ = get_basename_signals(source_signal_pairs, DATA_SOURCES_BY_ID, DATA_SIGNALS_BY_KEY)
            expected_basename_pairs = [
                SourceSignalPair(source="src", signal=["sig_base", "sig_base", "sig_base", "sig_base"]),
                SourceSignalPair(source="src2", signal=["sig"]),
            ]
            assert basename_pairs == expected_basename_pairs

        with self.subTest("resolve"):
            source_signal_pairs = [SourceSignalPair(source="src", signal=True)]
            basename_pairs, _ = get_basename_signals(source_signal_pairs, DATA_SOURCES_BY_ID, DATA_SIGNALS_BY_KEY)
            expected_basename_pairs = [SourceSignalPair("src", ["sig_base"] * 4)]
            assert basename_pairs == expected_basename_pairs

        with self.subTest("test base, diff, smooth"):
            data = CovidcastRecords(
                signals=["sig_base"] * 20 + ["sig_other"] * 5,
                time_values=chain(date_range("2021-05-01", "2021-05-10"), date_range("2021-05-21", "2021-05-30"), date_range("2021-05-01", "2021-05-05")),
                values=chain(range(20), range(5)),
                stderrs=chain(range(20), range(5)),
                sample_sizes=chain(range(20), range(5))
            ).as_dataframe()
            values = list(chain(range(10), [None] * 10, range(10, 20)))
            source_signal_pairs = [SourceSignalPair("src", ["sig_base", "sig_diff", "sig_other", "sig_smooth"])]
            _, row_transform_generator = get_basename_signals(source_signal_pairs, DATA_SOURCES_BY_ID, DATA_SIGNALS_BY_KEY)
            time_pairs = TimePair("day", [(20210501, 20210530)])
            idx = ["source", "signal", "time_value"]
            df_sorted = DataFrame.from_records(row_transform_generator(data.to_dict(orient="records"), time_pairs=time_pairs)).set_index(idx).sort_index()
            expected_df = (
                CovidcastRecords(
                    signals=["sig_base"] * 30 + ["sig_diff"] * 29 + ["sig_other"] * 30 + ["sig_smooth"] * 24,
                    time_values=chain(date_range("2021-05-01", "2021-05-30"), date_range("2021-05-02", "2021-05-30"), date_range("2021-05-01", "2021-05-30"), date_range("2021-05-07", "2021-05-30")),
                    values=chain(
                        values,
                        self._diff_rows(values),
                        chain(range(5), [None] * 25),
                        self._smooth_rows(values)
                    ),
                    stderrs=chain(
                        chain(range(10), [None] * 10, range(10, 20)),
                        chain([None] * 29),
                        chain(range(5), [None] * 25),
                        chain([None] * 24),
                    ),
                    sample_sizes=chain(
                        chain(range(10), [None] * 10, range(10, 20)),
                        chain([None] * 29),
                        chain(range(5), [None] * 25),
                        chain([None] * 24),
                    ),
                )
                .as_dataframe()
                .set_index(idx)
                .sort_index()
            )
            assert_frame_equal(df_sorted, expected_df)

        with self.subTest("test base, diff, smooth; multiple geos"):
            data = CovidcastRecords(
                signals=["sig_base"] * 40,
                geo_values=["ak"] * 20 + ["ca"] * 20,
                time_values=chain(date_range("2021-05-01", "2021-05-20"), date_range("2021-05-01", "2021-05-20")),
                values=chain(range(20), range(0, 40, 2)),
                stderrs=chain(range(20), range(0, 40, 2)),
                sample_sizes=chain(range(20), range(0, 40, 2))
            ).as_dataframe()
            source_signal_pairs = [SourceSignalPair("src", ["sig_base", "sig_diff", "sig_other", "sig_smooth"])]
            _, row_transform_generator = get_basename_signals(source_signal_pairs, DATA_SOURCES_BY_ID, DATA_SIGNALS_BY_KEY)
            idx = ["source", "signal", "time_value"]
            df = DataFrame.from_records(row_transform_generator(data.to_dict(orient="records"))).set_index(idx).sort_index()
            expected_df = (
                CovidcastRecords(
                    signals=["sig_base"] * 40 + ["sig_diff"] * 38 + ["sig_smooth"] * 28,
                    geo_values=["ak"] * 20 + ["ca"] * 20 + ["ak"] * 19 + ["ca"] * 19 + ["ak"] * 14 + ["ca"] * 14,
                    time_values=chain(
                        date_range("2021-05-01", "2021-05-20"),
                        date_range("2021-05-01", "2021-05-20"),
                        date_range("2021-05-02", "2021-05-20"),
                        date_range("2021-05-02", "2021-05-20"),
                        date_range("2021-05-07", "2021-05-20"),
                        date_range("2021-05-07", "2021-05-20")
                    ),
                    values=chain(
                        chain(range(20), range(0, 40, 2)),
                        chain([1] * 19, [2] * 19),
                        chain([sum(x) / len(x) for x in windowed(range(20), 7)], [sum(x) / len(x) for x in windowed(range(0, 40, 2), 7)])
                    ),
                    stderrs=chain(
                        chain(range(20), range(0, 40, 2)),
                        chain([None] * 38),
                        chain([None] * 28),
                    ),
                    sample_sizes=chain(
                        chain(range(20), range(0, 40, 2)),
                        chain([None] * 38),
                        chain([None] * 28),
                    )
                )
                .as_dataframe()
                .set_index(idx)
                .sort_index()
            )
            assert_frame_equal(df, expected_df)

        with self.subTest("resolve signals called"):
            data = CovidcastRecords(
                signals=["sig_base"] * 20 + ["sig_other"] * 5,
                time_values=chain(date_range("2021-05-01", "2021-05-10"), date_range("2021-05-21", "2021-05-30"), date_range("2021-05-01", "2021-05-05")),
                values=chain(range(20), range(5)),
                stderrs=chain(range(20), range(5)),
                sample_sizes=chain(range(20), range(5))
            ).as_dataframe()
            source_signal_pairs = [SourceSignalPair("src", True)]
            _, row_transform_generator = get_basename_signals(source_signal_pairs, DATA_SOURCES_BY_ID, DATA_SIGNALS_BY_KEY)
            time_pairs = TimePair("day", [(20210501, 20210530)])
            idx = ["source", "signal", "time_value"]
            df = DataFrame.from_records(row_transform_generator(data.to_dict(orient="records"), time_pairs=time_pairs)).set_index(idx).sort_index()
            expected_df = (
                CovidcastRecords(
                    signals=["sig_base"] * 30 + ["sig_diff"] * 29 + ["sig_diff_smooth"] * 23 + ["sig_other"] * 30 + ["sig_smooth"] * 24,
                    time_values=chain(
                        date_range("2021-05-01", "2021-05-30"),
                        date_range("2021-05-02", "2021-05-30"),
                        date_range("2021-05-08", "2021-05-30"),
                        date_range("2021-05-01", "2021-05-30"),
                        date_range("2021-05-07", "2021-05-30")
                    ),
                    values=chain(
                        chain(range(10), [None] * 10, range(10, 20)),
                        chain([1] * 9, [None] * 11, [1] * 9),
                        chain([sum(x) / len(x) if None not in x else None for x in windowed(chain([1] * 9, [None] * 11, [1] * 9), 7)]),
                        chain(range(5), [None] * 25),
                        chain([sum(x) / len(x) if None not in x else None for x in windowed(chain(range(10), [None] * 10, range(10, 20)), 7)])
                    ),
                    stderrs=chain(
                        chain(range(10), [None] * 10, range(10, 20)),
                        chain([None] * 29),
                        chain([None] * 23),
                        chain(range(5), [None] * 25),
                        chain([None] * 24),
                    ),
                    sample_sizes=chain(
                        chain(range(10), [None] * 10, range(10, 20)),
                        chain([None] * 29),
                        chain([None] * 23),
                        chain(range(5), [None] * 25),
                        chain([None] * 24),
                    )
                )
                .as_dataframe()
                .set_index(idx)
                .sort_index()
            )
            assert_frame_equal(df, expected_df)


        with self.subTest("empty iterator"):
            source_signal_pairs = [SourceSignalPair("src", ["sig_base", "sig_diff", "sig_smooth"])]
            _, row_transform_generator = get_basename_signals(source_signal_pairs, DATA_SOURCES_BY_ID, DATA_SIGNALS_BY_KEY)
            assert list(row_transform_generator({})) == []
