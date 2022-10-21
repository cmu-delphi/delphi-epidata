from datetime import datetime, timedelta
from functools import reduce
from math import inf
from numbers import Number
from pathlib import Path
from typing import Iterable, Optional, Union

# third party
import numpy as np
import pandas as pd
import pytest
import pytest_check as check
import requests

# first party
import delphi.operations.secrets as secrets
from delphi.epidata.acquisition.covidcast.covidcast_row import CovidcastRow
from delphi.epidata.acquisition.covidcast.database_meta import DatabaseMeta

# use the local instance of the Epidata API
BASE_URL = "http://delphi_web_epidata/epidata/api.php"
TEST_DATA_DIR = Path("repos/delphi/delphi-epidata/testdata/acquisition/covidcast/")


def _df_to_covidcastrows(df: pd.DataFrame) -> Iterable[CovidcastRow]:
    """Iterates over the rows of a dataframe.

    The dataframe is expected to have many columns, see below for which.
    """
    for _, row in df.iterrows():
        yield CovidcastRow(
            source=row.data_source if "data_source" in df.columns else row.source,
            signal=row.signal,
            time_type=row.time_type,
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


class TestCovidcastMeta:
    def setup_method(self):
        """Perform per-test setup."""

        # connect to the `epidata` database
        self.db = DatabaseMeta(base_url="http://delphi_web_epidata/epidata")
        self.db.connect(user="user", password="pass", host="delphi_database_epidata", database="covid")

        # TODO: Switch when delphi_epidata client is released.
        self.db.delphi_epidata = False

        # clear all tables
        self.db._cursor.execute("truncate table epimetric_load")
        self.db._cursor.execute("truncate table epimetric_full")
        self.db._cursor.execute("truncate table epimetric_latest")
        self.db._cursor.execute("truncate table geo_dim")
        self.db._cursor.execute("truncate table signal_dim")
        self.db._connection.commit()
        # reset the `covidcast_meta_cache` table (it should always have one row)
        self.db._cursor.execute('update covidcast_meta_cache set timestamp = 0, epidata = "[]"')

        self.db._connection.commit()

        # initialize counter for tables without non-autoincrement id
        self.id_counter = 666

        # use the local instance of the epidata database
        secrets.db.host = "delphi_database_epidata"
        secrets.db.epi = ("user", "pass")

    def teardown_method(self):
        """Perform per-test teardown."""
        self.db._cursor.close()
        self.db._connection.close()

    def _insert_rows(self, rows: Iterable[CovidcastRow]):
        self.db.insert_or_update_bulk(list(rows))
        self.db.run_dbjobs()
        self.db._connection.commit()
        return rows

    def get_source_signal_from_db(self, source: str, signal: str) -> pd.DataFrame:
        """Get the source signal data from the database."""
        sql = f"""SELECT c.signal, c.geo_type, c.geo_value, c.time_value, c.value FROM epimetric_latest_v c WHERE 1 = 1 AND c.`source` = '{source}' AND c.`signal` = '{signal}'"""
        self.db._cursor.execute(sql)
        df = (
            pd.DataFrame.from_records(self.db._cursor.fetchall(), columns=["signal", "geo_type", "geo_value", "time_value", "value"])
            .assign(time_value=lambda x: pd.to_datetime(x["time_value"], format="%Y%m%d"))
            .set_index(["signal", "geo_value", "time_value"])
            .sort_index()
        )
        return df

    def get_source_signal_from_api(self, source: str, signal: str) -> pd.DataFrame:
        """Query the source signal data from the local API."""
        base_url = "http://delphi_web_epidata/epidata/covidcast/"

        def get_api_df(**params) -> pd.DataFrame:
            return pd.DataFrame.from_records(requests.get(base_url, params=params).json()["epidata"])

        ALLTIME = "19000101-20500101"
        params = {"signal": f"{source}:{signal}", "geo": "state:*;county:*", "time": f"day:{ALLTIME}"}
        df = get_api_df(**params).assign(geo_type="day", time_value=lambda x: pd.to_datetime(x["time_value"], format="%Y%m%d")).set_index(["signal", "geo_value", "time_value"]).sort_index()
        return df

    def _insert_csv(self, filename: str):
        with pd.read_csv(filename, chunksize=10_000) as reader:
            for chunk_df in reader:
                self._insert_rows(_df_to_covidcastrows(chunk_df))

    @pytest.mark.skip("Archived.")
    @pytest.mark.parametrize("test_data_filepath", TEST_DATA_DIR.glob("*.csv"))
    def test_incidence(self, test_data_filepath):
        """This is large-scale A/B test of the JIT system for the incidence signal.

        It was tested on large datasets and found to be correct. See #646.

        Uses live API data and compares:
        - the results of the new JIT system to the API data
        - the results of the new JIT system to the Pandas-derived data
        """
        source = "usa-facts" if "usa-facts" in str(test_data_filepath) else "jhu-csse"
        print(test_data_filepath)
        self._insert_csv(test_data_filepath)

        # Here we load:
        #   test_data_full_df - the original CSV file with our test data
        #   db_pandas_incidence_df - the incidence data pulled from the database as cumulative, placed on a contiguous index (live data has gaps), and then diffed via Pandas
        #   api_incidence_df - the incidence data as returned by the API from JIT
        test_data_full_df = (
            pd.read_csv(test_data_filepath)
            .assign(time_value=lambda x: pd.to_datetime(x["time_value"]), geo_value=lambda x: x["geo_value"].astype(str))
            .set_index(["signal", "geo_value", "time_value"])
            .sort_index()
        )
        db_pandas_incidence_df = (
            self.get_source_signal_from_db(source, "confirmed_cumulative_num")
            # Place on a contiguous index
            .groupby(["signal", "geo_value"])
            .apply(lambda x: x.reset_index().drop(columns=["signal", "geo_value"]).set_index("time_value").reindex(pd.date_range("2020-01-25", "2022-09-10")))
            .reset_index()
            .rename(columns={"level_2": "time_value"})
            .set_index(["signal", "geo_value", "time_value"])
            # Diff
            .groupby(["signal", "geo_value"])
            .apply(lambda x: x["value"].reset_index().drop(columns=["signal", "geo_value"]).set_index("time_value").diff())
            .reset_index()
            .assign(signal="confirmed_incidence_num")
            .set_index(["signal", "geo_value", "time_value"])
        )
        api_incidence_df = self.get_source_signal_from_api(source, "confirmed_incidence_num")

        # Join into one dataframe for easy comparison
        test_data_full_df = test_data_full_df.join(db_pandas_incidence_df.value, rsuffix="_db_pandas")
        test_data_full_df = test_data_full_df.join(api_incidence_df.value, rsuffix="_api_jit")
        test_data_cumulative_df: pd.DataFrame = test_data_full_df.loc["confirmed_cumulative_num"]
        test_data_incidence_df: pd.DataFrame = test_data_full_df.loc["confirmed_incidence_num"]

        # Test 1: show that Pandas-recomputed incidence (from cumulative) is identical to JIT incidence (up to 7 decimal places).
        pandas_ne_jit = test_data_full_df[["value_db_pandas", "value_api_jit"]].dropna(how="any", axis=0)
        pandas_ne_jit = pandas_ne_jit[pandas_ne_jit.value_db_pandas.sub(pandas_ne_jit.value_api_jit, fill_value=inf).abs().ge(1e-7)]
        check.is_true(pandas_ne_jit.empty, "Check Pandas-JIT incidence match.")
        if not pandas_ne_jit.empty:
            print("Pandas-JIT incidence mismatch:")
            print(pandas_ne_jit.to_string())

        # Test 2: show that some JIT incidence values do not match live data. These are errors in the live data.
        live_ne_jit = test_data_full_df[["value", "value_api_jit"]].dropna(how="any", axis=0)
        live_ne_jit = live_ne_jit[live_ne_jit.value.sub(live_ne_jit.value_api_jit, fill_value=inf).abs().ge(1e-7)]
        check.is_true(live_ne_jit.empty, "Check JIT-live match.")
        if not live_ne_jit.empty:
            print("JIT-live mismatch:")
            print(live_ne_jit.to_string())

        # Test 3: show that when JIT has a NAN, it is reasonable: the cumulative signal is either missing today or yesterday.
        jit_nan_df = test_data_incidence_df[["value", "value_api_jit"]].query("value_api_jit.isna()")
        jit_nan_df = reduce(
            lambda x, y: pd.merge(x, y, how="outer", left_index=True, right_index=True),
            (
                test_data_cumulative_df.filter(items=jit_nan_df.index.map(lambda x: (x[0], x[1] - timedelta(days=i))), axis=0)["value"].rename(f"value_{i}_days_past")
                for i in range(2)
            ),
        )
        jit_nan_df = jit_nan_df[jit_nan_df.notna().all(axis=1)]
        check.is_true(jit_nan_df.empty, "Check JIT NANs are reasonable.")
        if not jit_nan_df.empty:
            print("JIT NANs are unreasonable:")
            print(jit_nan_df.to_string())

    @pytest.mark.skip("Too slow.")
    @pytest.mark.parametrize("test_data_filepath", TEST_DATA_DIR.glob("*.csv"))
    def test_7dav_incidence(self, test_data_filepath):
        """This is large-scale A/B test of the JIT system for the 7dav incidence signal.

        It was tested on large datasets and found to be correct. See #646.

        Uses live API data and compares:
        - the results of the new JIT system to the API data
        - the results of the new JIT system to the Pandas-derived data
        """
        source = "usa-facts" if "usa-facts" in str(test_data_filepath) else "jhu-csse"
        print(test_data_filepath)
        self._insert_csv(test_data_filepath)

        # Here we load:
        #   test_data_full_df - the original CSV file with our test data
        #   db_pandas_incidence_df - the incidence data pulled from the database as cumulative, placed on a contiguous index (live data has gaps), and then diffed via Pandas
        #   api_incidence_df - the incidence data as returned by the API from JIT
        test_data_full_df = (
            pd.read_csv(test_data_filepath)
            .assign(time_value=lambda x: pd.to_datetime(x["time_value"]), geo_value=lambda x: x["geo_value"].astype(str))
            .set_index(["signal", "geo_value", "time_value"])
            .sort_index()
        )
        db_pandas_7dav_incidence_df = (
            self.get_source_signal_from_db(source, "confirmed_cumulative_num")
            .groupby(["signal", "geo_value"])
            .apply(lambda x: x.reset_index().drop(columns=["signal", "geo_value"]).set_index("time_value").reindex(pd.date_range("2020-01-25", "2022-09-10")))
            .reset_index()
            .rename(columns={"level_2": "time_value"})
            .set_index(["signal", "geo_value", "time_value"])
            .groupby(["signal", "geo_value"])
            .apply(lambda x: x["value"].reset_index().drop(columns=["signal", "geo_value"]).set_index("time_value").diff().rolling(7).mean())
            .reset_index()
            .assign(signal="confirmed_7dav_incidence_num")
            .set_index(["signal", "geo_value", "time_value"])
        )
        api_7dav_incidence_df = self.get_source_signal_from_api(source, "confirmed_7dav_incidence_num")

        # Join into one dataframe for easy comparison
        test_data_full_df = test_data_full_df.join(db_pandas_7dav_incidence_df.value, rsuffix="_db_pandas")
        test_data_full_df = test_data_full_df.join(api_7dav_incidence_df.value, rsuffix="_api_jit")
        test_data_cumulative_df: pd.DataFrame = test_data_full_df.loc["confirmed_cumulative_num"]
        test_data_7dav_incidence_df: pd.DataFrame = test_data_full_df.loc["confirmed_7dav_incidence_num"]

        # Test 1: show that Pandas-recomputed incidence (from cumulative) is identical to JIT incidence (up to 7 decimal places).
        pandas_ne_jit = test_data_full_df[["value_db_pandas", "value_api_jit"]].dropna(how="any", axis=0)
        pandas_ne_jit = pandas_ne_jit[pandas_ne_jit.value_db_pandas.sub(pandas_ne_jit.value_api_jit, fill_value=inf).abs().ge(1e-7)]
        check.is_true(pandas_ne_jit.empty, "Check Pandas-JIT incidence match.")
        if not pandas_ne_jit.empty:
            print("Pandas-JIT incidence mismatch:")
            print(pandas_ne_jit.to_string())

        # Test 2: show that some JIT incidence values do not match live data. These are errors in the live data.
        live_ne_jit = test_data_7dav_incidence_df[["value", "value_api_jit"]].dropna(how="any", axis=0)
        live_ne_jit = live_ne_jit[live_ne_jit.value.sub(live_ne_jit.value_api_jit, fill_value=inf).abs().ge(1e-7)]
        check.is_true(live_ne_jit.empty, "Check JIT-live match.")
        if not live_ne_jit.empty:
            print("JIT-live mismatch:")
            print(live_ne_jit.to_string())

        # Test 3: show that when JIT has a NAN, it is reasonable: the cumulative signal is either missing today or yesterday.
        jit_nan_df = test_data_7dav_incidence_df[["value", "value_api_jit"]].query("value_api_jit.isna()")
        jit_nan_df = reduce(
            lambda x, y: pd.merge(x, y, how="outer", left_index=True, right_index=True),
            (
                test_data_cumulative_df.filter(items=jit_nan_df.index.map(lambda x: (x[0], x[1] - timedelta(days=i))), axis=0)["value"].rename(f"value_{i}_days_past")
                for i in range(8)
            ),
        )
        jit_nan_df = jit_nan_df.dropna(how="any", axis=0)
        check.is_true(jit_nan_df.empty, "Check JIT NANs are reasonable.")
        if not jit_nan_df.empty:
            print("JIT NANs are not reasonable:")
            print(jit_nan_df.to_string())
