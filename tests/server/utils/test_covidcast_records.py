import unittest
from dataclasses import asdict
from datetime import date

from pandas import DataFrame, date_range
from pandas.testing import assert_frame_equal

from delphi_utils.nancodes import Nans
from delphi.epidata.server.utils import date_to_time_value, apply_kwargs, CovidcastRecord, CovidcastRecordCompatibility, CovidcastRecords

class TestCovidcastRecords(unittest.TestCase):
    def test_apply_kwargs(self):
        def f(a=5, b=5):
            return (a, b)

        assert apply_kwargs(f, a=[3, 2]) == [(3, 5), (2, 5)]
        assert apply_kwargs(f, a=[3, 2], b=[1, 1]) == [(3, 1), (2, 1)]

    def test_CovidcastRecord(self):
        assert asdict(CovidcastRecord(source="src", value=5.0)) == {
            "source": "src",
            "signal": "sig",
            "geo_type": "state",
            "geo_value": "ca",
            "time_value": date_to_time_value(date(2021, 5, 1)),
            "value": 5.0,
            "stderr": 1.0,
            "sample_size": 1.0,
            "missing_value": Nans.NOT_MISSING,
            "missing_stderr": Nans.NOT_MISSING,
            "missing_sample_size": Nans.NOT_MISSING,
        }
        assert asdict(CovidcastRecordCompatibility(value=5.0)) == {
            "signal": "sig",
            "geo_type": "state",
            "geo_value": "ca",
            "time_value": date_to_time_value(date(2021, 5, 1)),
            "value": 5.0,
            "stderr": 1.0,
            "sample_size": 1.0,
            "missing_value": Nans.NOT_MISSING,
            "missing_stderr": Nans.NOT_MISSING,
            "missing_sample_size": Nans.NOT_MISSING,
        }

    def test_CovidcastRecords(self):
        df = CovidcastRecords(signals=["sig_base"] * 5 + ["sig_other"] * 5, time_values=date_range("2021-05-01", "2021-05-05").to_list() * 2, values=list(range(10))).as_dataframe()
        expected_df = DataFrame(
            {
                "source": ["src"] * 10,
                "signal": ["sig_base"] * 5 + ["sig_other"] * 5,
                "geo_type": ["state"] * 10,
                "geo_value": ["ca"] * 10,
                "time_value": map(date_to_time_value, date_range("2021-05-01", "2021-05-5").to_list() * 2),
                "value": range(10),
                "stderr": [1.0] * 10,
                "sample_size": [1.0] * 10,
                "missing_value": [Nans.NOT_MISSING] * 10,
                "missing_stderr": [Nans.NOT_MISSING] * 10,
                "missing_sample_size": [Nans.NOT_MISSING] * 10,
            }
        )
        assert_frame_equal(df, expected_df)

        df = CovidcastRecords(
            signals=["sig_base"] * 5 + ["sig_other"] * 5, time_values=date_range("2021-05-01", "2021-05-05").to_list() * 2, values=list(range(10)), is_compatibility=True
        ).as_dataframe()
        expected_df = DataFrame(
            {
                "signal": ["sig_base"] * 5 + ["sig_other"] * 5,
                "geo_type": ["state"] * 10,
                "geo_value": ["ca"] * 10,
                "time_value": map(date_to_time_value, date_range("2021-05-01", "2021-05-5").to_list() * 2),
                "value": range(10),
                "stderr": [1.0] * 10,
                "sample_size": [1.0] * 10,
                "missing_value": [Nans.NOT_MISSING] * 10,
                "missing_stderr": [Nans.NOT_MISSING] * 10,
                "missing_sample_size": [Nans.NOT_MISSING] * 10,
            }
        )
        assert_frame_equal(df, expected_df)
