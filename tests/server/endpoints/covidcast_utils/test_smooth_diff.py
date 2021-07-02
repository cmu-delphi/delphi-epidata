from pandas import DataFrame, to_datetime, date_range
from pandas.testing import assert_frame_equal
from numpy import NaN, allclose
from itertools import chain
from more_itertools import windowed

from delphi.epidata.server._params import SourceSignalPair
from delphi.epidata.server.endpoints.covidcast_utils.smooth_diff import generate_row_diffs, generate_smooth_rows, _smoother

class TestStreaming:
    def test__smoother(self):
        assert _smoother(list(range(7)), [1] * 7) == sum(range(7))
        assert _smoother([1] * 6, list(range(7))) == sum([1] * 6) / 6


    def test_generate_smooth_rows(self):
        def _windowed_slide(iterable, n):
            for e in windowed(chain(["_"] * (n - 1), iterable), n):
                yield tuple(filter(lambda x: x != "_", e))

        data = DataFrame({
            "timestamp": to_datetime(date_range("2021-05-01", "2021-05-26").to_list() * 2),
            "geo_type": ["state"] * 52,
            "geo_value": ["ak"] * 26 + ["ca"] * 26,
            "value": list(range(23)) + [NaN, 2.0, 1.0] + list(range(26, 52))
        })

        # dynamic window, no fill
        smoothed_df = DataFrame.from_records(generate_smooth_rows((x for x in data.to_dict(orient='records')), pad_fill_value=None))
        expected_df = DataFrame({
            "timestamp": to_datetime(date_range("2021-05-01", "2021-05-26").to_list() * 2),
            "geo_type": ["state"] * 52,
            "geo_value": ["ak"] * 26 + ["ca"] * 26,
            "value": (
                [_smoother(x) for x in _windowed_slide(chain(range(23), [NaN] * 3), 7)] +
                [_smoother(x) for x in _windowed_slide(range(26, 52), 7)]
            )
        })
        assert_frame_equal(smoothed_df, expected_df)

        # slide in window, fill on left with 0s
        smoothed_df = DataFrame.from_records(generate_smooth_rows((x for x in data.to_dict(orient='records')), pad_fill_value=0))
        expected_df = DataFrame({
            "timestamp": to_datetime(date_range("2021-05-01", "2021-05-26").to_list() * 2),
            "geo_type": ["state"] * 52,
            "geo_value": ["ak"] * 26 + ["ca"] * 26,
            "value": (
                [_smoother(x) for x in windowed(chain(6*[0], range(23), [NaN, 2.0, 1.0]), 7)] +
                [_smoother(x) for x in windowed(chain(6*[0], range(26, 52)), 7)]
            )
        })
        assert allclose(smoothed_df["value"].to_numpy(), expected_df["value"].to_numpy(), equal_nan=True)

        # same, but fill nan
        smoothed_df = DataFrame.from_records(generate_smooth_rows((x for x in data.to_dict(orient='records')), pad_fill_value=NaN, nan_fill_value=0))
        expected_df = DataFrame({
            "timestamp": to_datetime(date_range("2021-05-01", "2021-05-26").to_list() * 2),
            "geo_type": ["state"] * 52,
            "geo_value": ["ak"] * 26 + ["ca"] * 26,
            "value": (
                [_smoother(x) for x in windowed(chain(6*[0], range(23), [0, 2.0, 1.0]), 7)] +
                [_smoother(x) for x in windowed(chain(6*[0], range(26, 52)), 7)]
            )
        })
        assert allclose(smoothed_df["value"].to_numpy(), expected_df["value"].to_numpy(), equal_nan=True)

        # a dataframe a single entry should return unchanged, when dynamic
        data_one = DataFrame({
            "timestamp": to_datetime(date_range("2021-05-01", "2021-05-01").to_list()),
            "geo_type": ["state"],
            "geo_value": ["ca"],
            "value": [1.0]
        })
        smoothed_df = DataFrame.from_records(generate_smooth_rows((x for x in data_one.to_dict(orient='records'))))
        expected_df = data_one
        assert allclose(smoothed_df["value"].to_numpy(), expected_df["value"].to_numpy(), equal_nan=True)


    def test_generate_row_diffs(self):
        data = DataFrame({
            "timestamp": to_datetime(date_range("2021-05-01", "2021-05-26").to_list() * 2),
            "geo_type": ["state"] * 52,
            "geo_value": ["ak"] * 26 + ["ca"] * 26,
            "value": list(range(23)) + [NaN, 2.0, 1.0] + list(range(26, 52))
        })

        # no fill
        diffs_df = DataFrame.from_records(generate_row_diffs((x for x in data.to_dict(orient='records'))))
        expected_values = data.groupby("geo_value")["value"].diff()
        expected_values = expected_values.iloc[[x for x in set(range(52)) - {0, 26}]]
        assert allclose(diffs_df["value"], expected_values, equal_nan=True)

        # fill NaN
        diffs_df = DataFrame.from_records(generate_row_diffs((x for x in data.to_dict(orient='records')), pad_fill_value=NaN))
        expected_values = data.groupby("geo_value")["value"].diff()
        assert allclose(diffs_df["value"], expected_values, equal_nan=True)

        # fill 'first'
        diffs_df = DataFrame.from_records(generate_row_diffs((x for x in data.to_dict(orient='records')), pad_fill_value="first"))
        expected_values = data.groupby("geo_value")["value"].diff()
        expected_values.iloc[[0, 26]] = 0
        assert allclose(diffs_df["value"], expected_values, equal_nan=True)
