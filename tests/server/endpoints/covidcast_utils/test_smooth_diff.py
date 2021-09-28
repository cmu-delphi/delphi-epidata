from pandas import DataFrame, date_range
from pandas.testing import assert_frame_equal
from numpy import nan
from itertools import chain
from more_itertools import windowed

from delphi.epidata.server.utils import date_to_time_value, CovidcastRecords
from delphi.epidata.server.endpoints.covidcast_utils.smooth_diff import generate_row_diffs, generate_smooth_rows, _smoother


class TestStreaming:
    def test__smoother(self):
        assert _smoother(list(range(7)), [1] * 7) == sum(range(7))
        assert _smoother([1] * 6, list(range(7))) == sum([1] * 6) / 6


    def test_generate_smooth_rows(self):
        # an empty dataframe should return an empty dataframe
        data = DataFrame({})
        smoothed_df = DataFrame.from_records(generate_smooth_rows(data.to_dict(orient='records')))
        expected_df = DataFrame({})
        assert_frame_equal(smoothed_df, expected_df)

        # a dataframe with a single entry should return a single nan value
        data = CovidcastRecords(
            time_values=[20210501],
            values=[1.0]
        ).as_dataframe()
        smoothed_df = DataFrame.from_records(generate_smooth_rows(data.to_dict(orient='records')))
        expected_df = CovidcastRecords(
            time_values=[20210501],
            values=[None],
            stderrs=[None],
            sample_sizes=[None]
        ).as_dataframe()
        assert_frame_equal(smoothed_df, expected_df)

        data = CovidcastRecords(
            time_values=date_range("2021-05-01", "2021-05-10"),
            values=chain(range(7), [None, 2., 1.])
        ).as_dataframe()

        # regular window, nan fill
        smoothed_df = DataFrame.from_records(generate_smooth_rows(data.to_dict(orient='records')))
        expected_df = CovidcastRecords(
            time_values=date_range("2021-05-07", "2021-05-10"),
            values=(sum(x)/len(x) if None not in x else None for x in windowed(chain(range(7), [None, 2., 1.]), 7)),
            stderrs=[None]*4,
            sample_sizes=[None]*4,
        ).as_dataframe()
        assert_frame_equal(smoothed_df, expected_df)

        # regular window, 0 fill
        smoothed_df = DataFrame.from_records(generate_smooth_rows(data.to_dict(orient='records'), nan_fill_value=0.))
        expected_df = CovidcastRecords(
            time_values=date_range("2021-05-07", "2021-05-10"),
            values=(sum(x)/len(x) if None not in x else None for x in windowed(chain(range(7), [0., 2., 1.]), 7)),
            stderrs=[None]*4,
            sample_sizes=[None]*4,
        ).as_dataframe()
        assert_frame_equal(smoothed_df, expected_df)

        # regular window, different window length
        smoothed_df = DataFrame.from_records(generate_smooth_rows(data.to_dict(orient='records'), smoother_window_length = 8))
        expected_df = CovidcastRecords(
            time_values=date_range("2021-05-08", "2021-05-10"),
            values=(sum(x)/len(x) if None not in x else None for x in windowed(chain(range(7), [None, 2., 1.]), 8)),
            stderrs=[None]*3,
            sample_sizes=[None]*3,
        ).as_dataframe()
        assert_frame_equal(smoothed_df, expected_df)

        # regular window, different kernel
        smoothed_df = DataFrame.from_records(generate_smooth_rows(data.to_dict(orient='records'), smoother_kernel = list(range(8))))
        expected_df = CovidcastRecords(
            time_values=date_range("2021-05-08", "2021-05-10"),
            values=(sum([i * j for i, j in zip(x, range(8))])/len(x) if None not in x else None for x in windowed(chain(range(7), [None, 2., 1.]), 8)),
            stderrs=[None]*3,
            sample_sizes=[None]*3,
        ).as_dataframe()
        assert_frame_equal(smoothed_df, expected_df)

        # conflicting smoother args validation
        smoothed_df = DataFrame.from_records(generate_smooth_rows(data.to_dict(orient='records'), smoother_kernel=[1/7.]*7, smoother_window_length=10))
        expected_df = CovidcastRecords(
            time_values=date_range("2021-05-07", "2021-05-10"),
            values=(sum([i * j for i, j in zip(x, [1/7.]*7)]) if None not in x else None for x in windowed(chain(range(7), [None, 2., 1.]), 7)),
            stderrs=[None]*4,
            sample_sizes=[None]*4,
        ).as_dataframe()
        assert_frame_equal(smoothed_df, expected_df)


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
