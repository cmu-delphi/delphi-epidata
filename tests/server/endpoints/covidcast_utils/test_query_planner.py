from itertools import chain, groupby
from numpy import NaN, allclose
from pandas import DataFrame, to_datetime, date_range
from pandas.testing import assert_frame_equal

from delphi.epidata.server.endpoints.covidcast_utils.query_planner import repeat_iterator_generator


class TestIterablePrototype():
    def test_repeat_iterator_generator(self):
        data = DataFrame({
            "source": ["src"] * 10,
            "signal": ["sig1"] * 5 + ["sig2"] * 5,
            "timestamp": to_datetime(date_range("2021-05-01", "2021-05-5").to_list() * 2),
            "geo_type": ["state"] * 10,
            "geo_value": ["ca"] * 10,
            "value": list(range(10))
        })
        expected_df = DataFrame({
            "source": ["src"] * 20,
            "signal": ["sig1"] * 5 + ["sig2"] * 5 + ["sig1"] * 10,
            "timestamp": to_datetime(date_range("2021-05-01", "2021-05-5").to_list() * 4),
            "geo_type": ["state"] * 20,
            "geo_value": ["ca"] * 20,
            "value": list(range(10)) + list(range(5)) * 2,
            "_tag": [0] * 10 + [1] * 5 + [2] * 5
        })
        repeat_df = DataFrame.from_records(repeat_iterator_generator(data.to_dict(orient="records"), {("src", "sig1"): 3, ("src", "sig2"): 1, ("extra", "key"): 2}, lambda x: (x["source"], x["signal"])))
        assert_frame_equal(repeat_df, expected_df)


    def test_groupby_tag(self):
        data = DataFrame({
            "source": ["src"] * 10,
            "signal": ["sig1"] * 5 + ["sig2"] * 5,
            "timestamp": to_datetime(date_range("2021-05-01", "2021-05-5").to_list() * 2),
            "geo_type": ["state"] * 10,
            "geo_value": ["ca"] * 10,
            "value": list(range(10))
        })
        expected_df = DataFrame({
            "source": ["src"] * 20,
            "signal": ["sig1"] * 5 + ["sig2"] * 5 + ["sig1"] * 10,
            "timestamp": to_datetime(date_range("2021-05-01", "2021-05-5").to_list() * 4),
            "geo_type": ["state"] * 20,
            "geo_value": ["ca"] * 20,
            "value": list(range(10)) + list(range(5)) * 2,
            "_tag": [0] * 10 + [1] * 5 + [2] * 5
        })
        repeat_iterator = repeat_iterator_generator(data.to_dict(orient="records"), {("src", "sig1"): 3, ("src", "sig2"): 1, ("extra", "key"): 2}, lambda x: (x["source"], x["signal"]))
        groups_df = []
        for key, group in groupby(repeat_iterator, lambda row: (row["source"], row["signal"], row["_tag"])):
            groups_df.append(DataFrame.from_records(group))
        breakpoint()
        assert_frame_equal(repeat_df, expected_df)
