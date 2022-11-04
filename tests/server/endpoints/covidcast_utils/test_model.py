import unittest
from itertools import chain
from unittest.mock import patch

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from delphi.epidata.acquisition.covidcast.covidcast_row import CovidcastRows
from delphi.epidata.server._params import SourceSignalPair, TimePair
from delphi.epidata.server.endpoints.covidcast_utils.model import (
    DIFF,
    DIFF_SMOOTH,
    IDENTITY,
    SMOOTH,
    is_derived,
    get_base_signal_transform,
    reindex_iterable,
    get_day_range,
    get_pad_length,
    pad_time_pairs,
)
from delphi.epidata.server.endpoints.covidcast_utils.test_utils import DATA_SOURCES_BY_ID, DATA_SIGNALS_BY_KEY


@patch("delphi.epidata.server.endpoints.covidcast_utils.model.data_sources_by_id", DATA_SOURCES_BY_ID)
@patch("delphi.epidata.server.endpoints.covidcast_utils.model.data_signals_by_key", DATA_SIGNALS_BY_KEY)
class TestModel(unittest.TestCase):
    def test_reindex_iterable(self):
        # Trivial test.
        time_pairs = [(20210503, 20210508)]
        assert list(reindex_iterable([], time_pairs)) == []

        data = CovidcastRows.from_args(time_value=pd.date_range("2021-05-03", "2021-05-08").to_list()).api_row_df
        for time_pairs in [[TimePair("day", [(20210503, 20210508)])], [], None]:
            with self.subTest(f"Identity operations: {time_pairs}"):
                df = CovidcastRows.from_records(reindex_iterable(data.to_dict(orient="records"), time_pairs)).api_row_df
                assert_frame_equal(df, data)

        data = CovidcastRows.from_args(time_value=pd.date_range("2021-05-03", "2021-05-08").to_list() + pd.date_range("2021-05-11", "2021-05-14").to_list()).api_row_df
        with self.subTest("Non-trivial operations"):
            time_pairs = [TimePair("day", [(20210501, 20210513)])]

            df = CovidcastRows.from_records(reindex_iterable(data.to_dict(orient="records"), time_pairs)).api_row_df
            expected_df = CovidcastRows.from_args(
                time_value=pd.date_range("2021-05-03", "2021-05-13"),
                issue=pd.date_range("2021-05-03", "2021-05-08").to_list() + [None] * 2 + pd.date_range("2021-05-11", "2021-05-13").to_list(),
                lag=[0] * 6 + [None] * 2 + [0] * 3,
                value=chain([10.0] * 6, [None] * 2, [10.0] * 3),
                stderr=chain([10.0] * 6, [None] * 2, [10.0] * 3),
                sample_size=chain([10.0] * 6, [None] * 2, [10.0] * 3),
            ).api_row_df
            assert_frame_equal(df, expected_df)

            df = CovidcastRows.from_records(reindex_iterable(data.to_dict(orient="records"), time_pairs, fill_value=2.0)).api_row_df
            expected_df = CovidcastRows.from_args(
                time_value=pd.date_range("2021-05-03", "2021-05-13"),
                issue=pd.date_range("2021-05-03", "2021-05-08").to_list() + [None] * 2 + pd.date_range("2021-05-11", "2021-05-13").to_list(),
                lag=[0] * 6 + [None] * 2 + [0] * 3,
                value=chain([10.0] * 6, [2.0] * 2, [10.0] * 3),
                stderr=chain([10.0] * 6, [None] * 2, [10.0] * 3),
                sample_size=chain([10.0] * 6, [None] * 2, [10.0] * 3),
            ).api_row_df
            assert_frame_equal(df, expected_df)

    def test_is_derived(self):
        assert is_derived("src", "sig_smooth") is True
        assert is_derived("src", True) is False
        assert is_derived("src", "sig_base") is False

    def test_get_base_signal_transform(self):
        assert get_base_signal_transform(SourceSignalPair("src", ["sig_smooth"])) == (SourceSignalPair("src", ["sig_base"]), SMOOTH)
        assert get_base_signal_transform(SourceSignalPair("src", ["sig_diff_smooth"])) == (SourceSignalPair("src", ["sig_base"]), DIFF_SMOOTH)
        assert get_base_signal_transform(SourceSignalPair("src", ["sig_diff"])) == (SourceSignalPair("src", ["sig_base"]), DIFF)

        with pytest.raises(ValueError, match=r"A non-derived signal*"):
            get_base_signal_transform(SourceSignalPair("src", ["sig_base"]))
        with pytest.raises(ValueError, match=r"Unrecognized signal*"):
            get_base_signal_transform(SourceSignalPair("src", ["sig_unknown"]))

    def test_get_pad_length(self):
        assert get_pad_length(IDENTITY, smoother_window_length=7) == 0
        assert get_pad_length(SMOOTH, smoother_window_length=7) == 6
        assert get_pad_length(DIFF, smoother_window_length=7) == 1
        assert get_pad_length(SMOOTH, smoother_window_length=5) == 4
        assert get_pad_length(DIFF_SMOOTH, smoother_window_length=10) == 10

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

    def test_get_day_range(self):
        assert list(get_day_range([TimePair("day", [20210817])])) == [20210817]
        assert list(get_day_range([TimePair("day", [20210817, (20210810, 20210815)])])) == [20210810, 20210811, 20210812, 20210813, 20210814, 20210815, 20210817]
        assert list(get_day_range([TimePair("day", [(20210801, 20210805)]), TimePair("day", [(20210803, 20210807)])])) == [20210801, 20210802, 20210803, 20210804, 20210805, 20210806, 20210807]
