from collections import Counter
from itertools import groupby
from typing import Dict, Iterable
from pandas import DataFrame, to_datetime, date_range
from pandas.testing import assert_frame_equal

from delphi.epidata.server._params import SourceSignalPair
from delphi.epidata.server.endpoints.covidcast_utils.model import (
    IDENTITY,
    DIFF,
    SMOOTH,
    DIFF_SMOOTH,
    data_signals_by_key,
    _resolve_all_signals,
    _get_parent_transform,
    _get_signal_counts,
    _buffer_and_tag_iterator,
    create_source_signal_group_transform_mapper,
)

class TestStreaming:
    def test__resolve_all_signals(self):
        source_signal_pair = SourceSignalPair("jhu-csse", True)
        expected_source_signal_pair = SourceSignalPair(
            source="jhu-csse",
            signal=[
                "confirmed_cumulative_num",
                "confirmed_7dav_cumulative_num",
                "confirmed_7dav_cumulative_prop",
                "confirmed_7dav_incidence_num",
                "confirmed_7dav_incidence_prop",
                "confirmed_cumulative_prop",
                "confirmed_incidence_num",
                "confirmed_incidence_prop",
                "deaths_cumulative_num",
                "deaths_7dav_cumulative_num",
                "deaths_7dav_cumulative_prop",
                "deaths_7dav_incidence_num",
                "deaths_7dav_incidence_prop",
                "deaths_cumulative_prop",
                "deaths_incidence_num",
                "deaths_incidence_prop",
            ],
        )
        source_signal_pair = _resolve_all_signals(source_signal_pair)
        assert source_signal_pair == expected_source_signal_pair

    def test__get_parent_transform(self):
        derived_signals = {
            "indicator-combination-cases-deaths:confirmed_7dav_cumulative_num": ("indicator-combination-cases-deaths:confirmed_cumulative_num", SMOOTH),
            "indicator-combination-cases-deaths:confirmed_7dav_incidence_num": ("indicator-combination-cases-deaths:confirmed_cumulative_num", DIFF_SMOOTH),
            "indicator-combination-cases-deaths:confirmed_incidence_num": ("indicator-combination-cases-deaths:confirmed_cumulative_num", DIFF),
            "indicator-combination-cases-deaths:deaths_7dav_cumulative_num": ("indicator-combination-cases-deaths:deaths_cumulative_num", SMOOTH),
            "indicator-combination-cases-deaths:deaths_7dav_incidence_num": ("indicator-combination-cases-deaths:deaths_cumulative_num", DIFF_SMOOTH),
            "indicator-combination-cases-deaths:deaths_incidence_num": ("indicator-combination-cases-deaths:deaths_cumulative_num", DIFF),
            "google-symptoms:ageusia_smoothed_search": ("google-symptoms:ageusia_raw_search", SMOOTH),
            "google-symptoms:anosmia_smoothed_search": ("google-symptoms:anosmia_raw_search", SMOOTH),
            "google-symptoms:sum_anosmia_ageusia_smoothed_search": ("google-symptoms:sum_anosmia_ageusia_raw_search", SMOOTH),
            "jhu-csse:confirmed_7dav_cumulative_num": ("jhu-csse:confirmed_cumulative_num", SMOOTH),
            "jhu-csse:confirmed_7dav_incidence_num": ("jhu-csse:confirmed_cumulative_num", DIFF_SMOOTH),
            "jhu-csse:confirmed_incidence_num": ("jhu-csse:confirmed_cumulative_num", DIFF),
            "jhu-csse:deaths_7dav_cumulative_num": ("jhu-csse:deaths_cumulative_num", SMOOTH),
            "jhu-csse:deaths_7dav_incidence_num": ("jhu-csse:deaths_cumulative_num", DIFF_SMOOTH),
            "jhu-csse:deaths_incidence_num": ("jhu-csse:deaths_cumulative_num", DIFF),
            "usa-facts:confirmed_7dav_cumulative_num": ("usa-facts:confirmed_cumulative_num", SMOOTH),
            "usa-facts:confirmed_7dav_incidence_num": ("usa-facts:confirmed_cumulative_num", DIFF_SMOOTH),
            "usa-facts:confirmed_incidence_num": ("usa-facts:confirmed_cumulative_num", DIFF),
            "usa-facts:deaths_7dav_cumulative_num": ("usa-facts:deaths_cumulative_num", SMOOTH),
            "usa-facts:deaths_7dav_incidence_num": ("usa-facts:deaths_cumulative_num", DIFF_SMOOTH),
            "usa-facts:deaths_incidence_num": ("usa-facts:deaths_cumulative_num", DIFF),
        }
        for signal_key in data_signals_by_key:
            signal = data_signals_by_key[signal_key]
            transform = _get_parent_transform(signal, data_signals_by_key) if signal.compute_from_base else IDENTITY
            derived_key = f"{signal_key[0]}:{signal_key[1]}"
            derived_signal = derived_signals.get(derived_key)
            expected_transform = derived_signals[derived_key][1] if derived_signal else IDENTITY
            assert transform == expected_transform


    def test__buffer_and_tag_iterator(self):
        data = DataFrame(
            {
                "source": ["src"] * 10,
                "signal": ["sig1"] * 5 + ["sig2"] * 5,
                "timestamp": to_datetime(date_range("2021-05-01", "2021-05-5").to_list() * 2),
                "geo_type": ["state"] * 10,
                "geo_value": ["ca"] * 10,
                "value": list(range(10)),
            }
        )
        signal_counts = {("src", "sig1"): 3, ("src", "sig2"): 1, ("extra", "key"): 2}
        expected_df = DataFrame(
            {
                "source": ["src"] * 20,
                "signal": ["sig1"] * 5 + ["sig2"] * 5 + ["sig1"] * 10,
                "timestamp": to_datetime(date_range("2021-05-01", "2021-05-5").to_list() * 4),
                "geo_type": ["state"] * 20,
                "geo_value": ["ca"] * 20,
                "value": list(range(10)) + list(range(5)) * 2,
                "_tag": [0] * 10 + [1] * 5 + [2] * 5,
            }
        )
        repeat_df = DataFrame.from_records(
            _buffer_and_tag_iterator(
                data.to_dict(orient="records"), signal_counts, lambda x: (x["source"], x["signal"])
            )
        )
        assert_frame_equal(repeat_df, expected_df)

        repeat_iterator = _buffer_and_tag_iterator(
            data.to_dict(orient="records"), signal_counts, lambda x: (x["source"], x["signal"])
        )
        groups_df = []
        for key, group in groupby(repeat_iterator, lambda row: (row["source"], row["signal"], row["_tag"])):
            groups_df.append(DataFrame.from_records(group))
        assert_frame_equal(groups_df[0].reset_index(drop=True), expected_df.iloc[0:5].reset_index(drop=True))
        assert_frame_equal(groups_df[1].reset_index(drop=True), expected_df.iloc[5:10].reset_index(drop=True))
        assert_frame_equal(groups_df[2].reset_index(drop=True), expected_df.iloc[10:15].reset_index(drop=True))
        assert_frame_equal(groups_df[3].reset_index(drop=True), expected_df.iloc[15:20].reset_index(drop=True))

        signal_counts = {}
        repeat_iterator = _buffer_and_tag_iterator(
            data.to_dict(orient="records"), signal_counts, lambda x: (x["source"], x["signal"])
        )
        repeat_df = DataFrame.from_records(repeat_iterator).drop(columns="_tag")
        expected_df = data
        assert_frame_equal(repeat_df, expected_df)

        repeat_iterator = _buffer_and_tag_iterator({}, signal_counts, lambda x: (x["source"], x["signal"]))
        assert list(repeat_iterator) == []

    def test__get_signal_counts(self):
        source_signal_pairs1 = [SourceSignalPair("src1", ["sig1", "sig2", "sig1", "sig1", "sig2"]), SourceSignalPair("src2", ["sig1"])]
        signal_counts = _get_signal_counts(source_signal_pairs1)
        expected_signal_counts = Counter({("src1", "sig1"): 3, ("src1", "sig2"): 2, ("src2", "sig1"): 1})
        assert signal_counts == expected_signal_counts

    def test_create_source_signal_group_transform_mapper(self):
        source_signal_pair = SourceSignalPair(
            source="jhu-csse",
            signal=[
                "confirmed_cumulative_num",
                "confirmed_7dav_cumulative_num",
                "confirmed_7dav_cumulative_prop",
                "confirmed_7dav_incidence_num",
                "confirmed_7dav_incidence_prop",
                "confirmed_cumulative_prop",
                "confirmed_incidence_num",
                "confirmed_incidence_prop",
                "deaths_cumulative_num",
                "deaths_7dav_cumulative_num",
                "deaths_7dav_cumulative_prop",
                "deaths_7dav_incidence_num",
                "deaths_7dav_incidence_prop",
                "deaths_cumulative_prop",
                "deaths_incidence_num",
                "deaths_incidence_prop",
            ],
        )
        [transformed_pairs], transform_group, map_row, iterator_buffer = create_source_signal_group_transform_mapper([source_signal_pair])
        dummy_iterable: Iterable[Dict] = [{"src1": 1}]

        for i, signal in enumerate(transformed_pairs.signal):
            # check that map_row returns the appropriate signal names back
            assert map_row("jhu-csse", signal, i) == source_signal_pair.signal[i]
            # if map_row does no aliasing, make sure that transform_group is the identity mapping
            if map_row("jhu-csse", signal, i) == signal[i]:
                assert transform_group("jhu-csse", signal, i, dummy_iterable) == dummy_iterable

        source_signal_pair = SourceSignalPair(
            source="src1",
            signal=True)
        [transformed_pairs], transform_group, map_row, iterator_buffer = create_source_signal_group_transform_mapper([source_signal_pair])
        assert transformed_pairs == source_signal_pair
