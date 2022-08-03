"""Unit tests for covidcast_meta_cache_updater.py."""

# standard library
import argparse

from datetime import date, datetime
from numbers import Number
from typing import Iterable, Optional, Union
import unittest
from unittest.mock import MagicMock

# third party
import pandas as pd
import numpy as np

from delphi.epidata.acquisition.covidcast.covidcast_meta_cache_updater import get_argument_parser, main
from delphi.epidata.acquisition.covidcast.database import CovidcastRow
from delphi.epidata.acquisition.covidcast.database_meta import DatabaseMeta


def _df_to_covidcastrows(df: pd.DataFrame) -> Iterable[CovidcastRow]:
    """Iterates over the rows of a dataframe.

    The dataframe is expected to have many columns, see below for which.
    """
    for x in df.iterrows():
        _, row = x
        yield CovidcastRow(
            source=row.data_source,
            signal=row.signal,
            time_type="day",
            geo_type=row.geo_type,
            time_value=datetime.strptime(row.time_value, "%Y-%m-%d"),
            geo_value=row.geo_value,
            value=row.value,
            stderr=row.stderr if not np.isnan(row.stderr) else None,
            sample_size=row.sample_size if not np.isnan(row.sample_size) else None,
            missing_value=row.missing_value,
            missing_stderr=row.missing_stderr,
            missing_sample_size=row.missing_sample_size,
            issue=datetime.strptime(row.issue, "%Y-%m-%d"),
            lag=row.lag,
        )

def _almost_equal(v1: Optional[Union[Number, str]], v2: Optional[Union[Number, str]], atol: float = 1e-08) -> bool:
    if v1 is None and v2 is None:
        return True
    elif (v1 is None and v2 is not None) or (v1 is not None and v2 is None):
        return False
    else:
        return np.allclose(v1, v2, atol=atol) if isinstance(v1, Number) and isinstance(v2, Number) else v1 == v2
 
def _dicts_equal(d1: dict, d2: dict, ignore_keys: Optional[list] = None, atol: float = 1e-08) -> bool:
    """Compare dictionary values using floating point comparison for numeric values."""
    assert set(d1.keys()) == set(d2.keys())
    return all(_almost_equal(d1.get(key), d2.get(key), atol=atol) for key in d1.keys() if (ignore_keys and key not in ignore_keys))


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    def setUp(self):
        """Perform per-test setup."""

        # connect to the `epidata` database
        self.db = DatabaseMeta(base_url="http://delphi_web_epidata/epidata")
        self.db.connect(user="user", password="pass", host="delphi_database_epidata")

        # TODO: Switch when delphi_epidata client is released.
        self.db.delphi_epidata = False

        # clear all tables
        self.db._cursor.execute("truncate table signal_load")
        self.db._cursor.execute("truncate table signal_history")
        self.db._cursor.execute("truncate table signal_latest")
        self.db._cursor.execute("truncate table geo_dim")
        self.db._cursor.execute("truncate table signal_dim")
        self.db.commit()

    def tearDown(self):
        """Perform per-test teardown."""
        self.db.disconnect(None)

    def _insert_csv(self, filename: str):
        self._insert_rows(_df_to_covidcastrows(pd.read_csv(filename)))

    def _insert_rows(self, rows: Iterable[CovidcastRow]):
        self.db.insert_or_update_bulk(list(rows))
        self.db.run_dbjobs()
        self.db._connection.commit()
        return rows

    def test_get_argument_parser(self):
        """Return a parser for command-line arguments."""
        self.assertIsInstance(get_argument_parser(), argparse.ArgumentParser)

    def test_main_successful(self):
        """Run the main program successfully."""

        api_response = {
            "result": 1,
            "message": "yes",
            "epidata": [{"foo": "bar"}],
        }

        args = MagicMock(log_file="log")
        mock_epidata_impl = MagicMock()
        mock_epidata_impl.covidcast_meta.return_value = api_response
        mock_database = MagicMock()
        mock_database.compute_covidcast_meta.return_value = api_response["epidata"]
        fake_database_impl = lambda: mock_database

        main(args, epidata_impl=mock_epidata_impl, database_impl=fake_database_impl)

        self.assertTrue(mock_database.connect.called)

        self.assertTrue(mock_database.update_covidcast_meta_cache.called)
        actual_args = mock_database.update_covidcast_meta_cache.call_args[0]
        expected_args = (api_response["epidata"],)
        self.assertEqual(actual_args, expected_args)

        self.assertTrue(mock_database.disconnect.called)
        self.assertTrue(mock_database.disconnect.call_args[0][0])

    def test_main_failure(self):
        """Run the main program with a query failure."""
        api_response = {
            "result": -123,
            "message": "no",
        }

        args = MagicMock(log_file="log")
        mock_database = MagicMock()
        mock_database.compute_covidcast_meta.return_value = list()
        fake_database_impl = lambda: mock_database

        main(args, epidata_impl=None, database_impl=fake_database_impl)

        self.assertTrue(mock_database.compute_covidcast_meta.called)

    def test_meta_values(self):
        """This test provides a framework for A/B testing between the old meta compute approach and the new one which relies on an API call for JIT signals.
        
        Uses a piece of the real data from the API to compare the results.

        test-data1.csv was generated with 

        >>> start_day = date(2020, 1, 20)
        >>> end_day = date(2020, 5, 1)
        >>> df = pd.concat([ 
            covidcast.signal(data_source="jhu-csse", signal="confirmed_cumulative_num", start_day=start_day, end_day=end_day, time_type="day", geo_type="state", geo_values="ak,ca"),
            covidcast.signal(data_source="jhu-csse", signal="confirmed_cumulative_num", start_day=start_day, end_day=end_day, time_type="day", geo_type="county", geo_values="02100,06003,06017,06027"),
            covidcast.signal(data_source="jhu-csse", signal="confirmed_incidence_num", start_day=start_day, end_day=end_day, time_type="day", geo_type="state", geo_values="ak,ca"),
            covidcast.signal(data_source="jhu-csse", signal="confirmed_incidence_num", start_day=start_day, end_day=end_day, time_type="day", geo_type="county", geo_values="02100,06003,06017,06027"),
            covidcast.signal(data_source="jhu-csse", signal="confirmed_7dav_incidence_num", start_day=start_day, end_day=end_day, time_type="day", geo_type="state", geo_values="ak,ca"),
            covidcast.signal(data_source="jhu-csse", signal="confirmed_7dav_incidence_num", start_day=start_day, end_day=end_day, time_type="day", geo_type="county", geo_values="02100,06003,06017,06027")
        ])
        >>> df.to_csv("test-data.csv")

        test-data2.csv was generated with (just a start_day difference, to match with 7dav)

        >>> end_day = date(2020, 5, 1)
        >>> df = pd.concat([ 
            covidcast.signal(data_source="jhu-csse", signal="confirmed_cumulative_num", start_day=date(2020, 2, 13), end_day=end_day, time_type="day", geo_type="state", geo_values="ak,ca"),
            covidcast.signal(data_source="jhu-csse", signal="confirmed_cumulative_num", start_day=date(2020, 2, 13), end_day=end_day, time_type="day", geo_type="county", geo_values="02100,06003,06017,06027"),
            covidcast.signal(data_source="jhu-csse", signal="confirmed_incidence_num", start_day=date(2020, 2, 14), end_day=end_day, time_type="day", geo_type="state", geo_values="ak,ca"),
            covidcast.signal(data_source="jhu-csse", signal="confirmed_incidence_num", start_day=date(2020, 2, 14), end_day=end_day, time_type="day", geo_type="county", geo_values="02100,06003,06017,06027"),
            covidcast.signal(data_source="jhu-csse", signal="confirmed_7dav_incidence_num", start_day=date(2020, 2, 20), end_day=end_day, time_type="day", geo_type="state", geo_values="ak,ca"),
            covidcast.signal(data_source="jhu-csse", signal="confirmed_7dav_incidence_num", start_day=date(2020, 2, 20), end_day=end_day, time_type="day", geo_type="county", geo_values="02100,06003,06017,06027")
        ])
        >>> df.to_csv("test-data.csv")
        """
        self._insert_csv("repos/delphi/delphi-epidata/tests/acquisition/covidcast/test-data/test-data2.csv")

        meta_values = self.db.compute_covidcast_meta(jit=False)
        meta_values2 = self.db.compute_covidcast_meta(jit=True, parallel=False)

        # This doesn't work because they are not exactly equal.
        # assert meta_values == meta_values2
        # 1. We have a difference in the min_lag, because JIT computes the lag differently.
        # 2. We have a numerical difference, because the existing indicators don't seem to compute smooth-diffed entries correctly (see below).

        df1 = pd.read_csv("repos/delphi/delphi-epidata/tests/acquisition/covidcast/test-data/test-data2.csv").query("signal == 'confirmed_cumulative_num' & geo_value == 'ca' & '2020-02-10' <= time_value <= '2020-02-26'")
        df2 = pd.read_csv("repos/delphi/delphi-epidata/tests/acquisition/covidcast/test-data/test-data2.csv").query("signal == 'confirmed_7dav_incidence_num' & geo_value == 'ca' & '2020-02-10' <= time_value <= '2020-02-26'")
        df = pd.merge(
            df1.assign(smooth_diffed = df1.value.diff().rolling(7).mean())[["time_value", "smooth_diffed"]],
            df2[["time_value", "value"]],
            on = "time_value"
        )
        # This SHOULD be zero, but it's not.
        assert df.smooth_diffed.sub(df.value).abs().sum() > 0

        # Ignore these issues, we have a match on this dataset.
        out = [_dicts_equal(x, y, ignore_keys=["min_lag"], atol=1.5) for x, y in zip(meta_values, meta_values2)]
        assert all(out)

        # TODO: The parallelized version of the code is not written yet, but should be simple once we're confident in the non-parallel version.
        # meta_values3 = self.db.compute_covidcast_meta(jit=True, parallel=True)
        # assert meta_values == meta_values3

    def test_meta_values2(self):
        """This is an A/B test between the old meta compute approach and the new one which relies on an API call for JIT signals.

        It relies on synthetic data that attempts to be as realistic and as general as possible.
        """
        def get_rows_gen(df: pd.DataFrame, filter_nans: bool = False) -> Iterable[CovidcastRow]:
            for args in df.itertuples(index=False):
                if not filter_nans or (filter_nans and not any(map(pd.isna, args._asdict().values()))):
                    yield CovidcastRow(**args._asdict())

        start_date = date(2022, 4, 1)
        end_date = date(2022, 6, 1)
        n = (end_date - start_date).days + 1

        # TODO: Build a more complex synthetic dataset here.
        cumulative_df = pd.DataFrame({
            "source": ["jhu-csse"] * n,
            "signal": ["confirmed_cumulative_num"] * n,
            "time_value": pd.date_range(start_date, end_date),
            "issue": pd.date_range(start_date, end_date),
            "value": list(range(n))
        })
        incidence_df = cumulative_df.assign(signal = "confirmed_incidence_num", value = cumulative_df.value.diff(), issue=[max(window) if window.size >= 2 else np.nan for window in cumulative_df.issue.rolling(2)])
        smoothed_incidence_df = incidence_df.assign(signal = "confirmed_7dav_incidence_num", value = incidence_df.value.rolling(7).mean(), issue=[max(window) if window.size >= 7 else np.nan for window in incidence_df.issue.rolling(7)])

        self._insert_rows(get_rows_gen(cumulative_df, filter_nans=True))
        self._insert_rows(get_rows_gen(incidence_df, filter_nans=True))
        self._insert_rows(get_rows_gen(smoothed_incidence_df, filter_nans=True))

        meta_values = self.db.compute_covidcast_meta(jit=False)
        meta_values2 = self.db.compute_covidcast_meta(jit=True, parallel=False)

        out = [_dicts_equal(x, y, ignore_keys=["max_lag"]) for x, y in zip(meta_values, meta_values2)]

        assert meta_values == meta_values2
