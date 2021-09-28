from pandas import DataFrame, date_range
from pandas.testing import assert_frame_equal
from numpy import nan
from itertools import chain
from more_itertools import windowed

from delphi.epidata.server.utils import date_to_time_value, CovidcastRecords
from delphi.epidata.server.endpoints.covidcast_utils.smooth_diff import generate_row_diffs, generate_smooth_rows


class TestStreaming:


    def test_generate_row_diffs(self):
        # an empty dataframe should return an empty dataframe
        data = DataFrame({})
        diffs_df = DataFrame.from_records(generate_row_diffs(data.to_dict(orient='records')))
        expected_df = DataFrame({})
        assert_frame_equal(diffs_df, expected_df)

        # a dataframe with a single entry should return a single nan value
        data = CovidcastRecords(
            time_values=[20210501],
            values=[1.0]
        ).as_dataframe()
        diffs_df = DataFrame.from_records(generate_row_diffs(data.to_dict(orient='records')))
        expected_df = CovidcastRecords(
            time_values=[20210501],
            values=[None],
            stderrs=[None],
            sample_sizes=[None]
        ).as_dataframe()
        assert_frame_equal(diffs_df, expected_df)

        data = CovidcastRecords(
            time_values=date_range("2021-05-01", "2021-05-10"),
            values=chain(range(7), [None, 2., 1.])
        ).as_dataframe()

        # no fill
        diffs_df = DataFrame.from_records(generate_row_diffs(data.to_dict(orient='records')))
        expected_df = CovidcastRecords(
            time_values=date_range("2021-05-02", "2021-05-10"),
            values=[1.] * 6 + [None, None, -1.],
            stderrs=[None] * 9,
            sample_sizes=[None] * 9
        ).as_dataframe()
        assert_frame_equal(diffs_df, expected_df)
