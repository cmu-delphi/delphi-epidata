"""Integration tests for the custom `covidcast/*` endpoints."""

# standard library
import csv
from copy import copy
from io import StringIO
from itertools import accumulate, chain
from typing import List
import numpy as np

# third party
import pandas as pd
import pytest
import requests

from delphi.epidata.acquisition.covidcast.covidcast_meta_cache_updater import main as update_cache
from delphi.epidata.acquisition.covidcast.covidcast_row import CovidcastRow, CovidcastRows, assert_frame_equal_no_order
from delphi.epidata.acquisition.covidcast.test_utils import CovidcastBase
from delphi.epidata.server.endpoints.covidcast_utils.test_utils import diff_df, reindex_df, diff_smooth_df
from delphi.epidata.server.utils.dates import iterate_over_range, iso_to_time_value

# use the local instance of the Epidata API
BASE_URL = "http://delphi_web_epidata/epidata/covidcast"
BASE_URL_OLD = "http://delphi_web_epidata/epidata/api.php"


def _read_csv_str(txt: str) -> pd.DataFrame:
    def gen(rows):
        for row in rows:
            row["value"] = float(row["value"]) if row["value"] else np.nan
            row["stderr"] = float(row["stderr"]) if row["stderr"] else np.nan
            row["sample_size"] = float(row["sample_size"]) if row["sample_size"] else np.nan
            row["time_value"] = iso_to_time_value(row["time_value"])
            row["issue"] = iso_to_time_value(row["issue"]) if row["issue"] else np.nan
            row["lag"] = int(row["lag"]) if row["lag"] else np.nan
            row["geo_value"] = str(row["geo_value"]).zfill(5)
            del row[""]
            if "data_source" in row:
                row["source"] = row["data_source"]
                del row["data_source"]
            yield row

    with StringIO(txt) as f:
        return CovidcastRows.from_records(gen(csv.DictReader(f))).db_row_df

class CovidcastEndpointTests(CovidcastBase):
    """Tests the `covidcast/*` endpoint."""

    def localSetUp(self):
        """Perform per-test setup."""
        # reset the `covidcast_meta_cache` table (it should always have one row)
        self._db._cursor.execute('update covidcast_meta_cache set timestamp = 0, epidata = "[]"')

    def _fetch(self, endpoint="/", is_compatibility=False, **params):
        # make the request
        if is_compatibility:
            url = BASE_URL_OLD
            params.setdefault("endpoint", "covidcast")
            if params.get("source"):
                params.setdefault("data_source", params.get("source"))
        else:
            url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def test_basic(self):
        """Request a signal from the / endpoint."""

        rows = [CovidcastRow(time_value=20200401 + i, value=i) for i in range(10)]
        first = rows[0]
        self._insert_rows(rows)

        with self.subTest("validation"):
            out = self._fetch("/")
            self.assertEqual(out["result"], -1)

        with self.subTest("simple"):
            out = self._fetch("/", signal=first.signal_pair, geo=first.geo_pair, time="day:*")
            self.assertEqual(len(out["epidata"]), len(rows))

        with self.subTest("unknown signal"):
            rows = [CovidcastRow(source="jhu-csse", signal="confirmed_unknown", time_value=20200401 + i, value=i) for i in range(10)]
            first = rows[0]
            self._insert_rows(rows)

            out = self._fetch("/", signal="jhu-csse:confirmed_unknown", geo=first.geo_pair, time="day:*")
            out_values = [row["value"] for row in out["epidata"]]
            expected_values = [float(row.value) for row in rows]
            self.assertEqual(out_values, expected_values)

    def test_compatibility(self):
        """Request at the /api.php endpoint."""
        rows = [CovidcastRow(source="src", signal="sig", time_value=20200401 + i, value=i) for i in range(10)]
        first = rows[0]
        self._insert_rows(rows)

        with self.subTest("simple"):
            # TODO: These tests aren't actually testing the compatibility endpoint.
            out = self._fetch("/", signal=first.signal_pair, geo=first.geo_pair, time="day:*")
            self.assertEqual(len(out["epidata"]), len(rows))

        with self.subTest("unknown signal"):
            rows = [CovidcastRow(source="jhu-csse", signal="confirmed_unknown", time_value=20200401 + i, value=i) for i in range(10)]
            first = rows[0]
            self._insert_rows(rows)

            out = self._fetch("/", signal="jhu-csse:confirmed_unknown", geo=first.geo_pair, time="day:*")
            out_values = [row["value"] for row in out["epidata"]]
            expected_values = [float(row.value) for row in rows]
            self.assertEqual(out_values, expected_values)

    # JIT tests
    def test_derived_signals(self):
        # The base signal data.
        data1 = CovidcastRows.from_args(
            source = ["jhu-csse"] * 10,
            signal = ["confirmed_cumulative_num"] * 10,
            time_value = iterate_over_range(20200401, 20200410, inclusive=True),
            geo_value = ["01"] * 10,
            value = [i ** 2 for i in range(10)],
        )
        data2 = CovidcastRows.from_args(
            source = ["jhu-csse"] * 10,
            signal = ["confirmed_cumulative_num"] * 10,
            time_value = iterate_over_range(20200401, 20200410, inclusive=True),
            geo_value = ["02"] * 10,
            value = [2 * i ** 2 for i in range(10)],
        )
        # A base signal with a time gap.
        data3 = CovidcastRows.from_args(
            source = ["jhu-csse"] * 15,
            signal = ["confirmed_cumulative_num"] * 15,
            time_value = chain(iterate_over_range(20200401, 20200410, inclusive=True), iterate_over_range(20200416, 20200420, inclusive=True)),
            geo_value = ["03"] * 15,
            value = [i ** 2 for i in chain(range(10), range(15, 20))],
        )
        # Insert rows into database.
        self._insert_rows(data1.rows + data2.rows + data3.rows)
        # Fill the gap in data3.
        data3_reindexed = reindex_df(data3.api_row_df)
        data_df = pd.concat([data1.api_row_df, data2.api_row_df, data3_reindexed])
        # Get the expected derived signal values.
        expected_diffed_df = diff_df(data_df, "confirmed_incidence_num").set_index(["signal", "geo_value", "time_value"])
        expected_smoothed_df = diff_smooth_df(data_df, "confirmed_7dav_incidence_num").set_index(["signal", "geo_value", "time_value"])
        expected_df = pd.concat([data_df.set_index(["signal", "geo_value", "time_value"]) , expected_diffed_df, expected_smoothed_df])

        with self.subTest("diffed signal"):
            out = self._fetch("/", signal="jhu-csse:confirmed_incidence_num", geo="county:01", time="day:20200401-20200410")
            out_df = CovidcastRows.from_records(out["epidata"]).api_row_df.set_index(["signal", "geo_value", "time_value"])
            merged_df = pd.merge(out_df, expected_df, left_index=True, right_index=True, suffixes=["_out", "_expected"])[["value_out", "value_expected"]]
            assert merged_df.empty is False
            assert merged_df.value_out.to_numpy() == pytest.approx(merged_df.value_expected, nan_ok=True)

        with self.subTest("diffed signal, multiple geos"):
            out = self._fetch("/", signal="jhu-csse:confirmed_incidence_num", geo="county:01,02", time="day:20200401-20200410")
            out_df = CovidcastRows.from_records(out["epidata"]).api_row_df.set_index(["signal", "geo_value", "time_value"])
            merged_df = pd.merge(out_df, expected_df, left_index=True, right_index=True, suffixes=["_out", "_expected"])[["value_out", "value_expected"]]
            assert merged_df.empty is False
            assert merged_df.value_out.to_numpy() == pytest.approx(merged_df.value_expected, nan_ok=True)

        with self.subTest("smooth diffed signal"):
            out = self._fetch("/", signal="jhu-csse:confirmed_7dav_incidence_num", geo="county:01,02", time="day:20200401-20200410")
            out_df = CovidcastRows.from_records(out["epidata"]).api_row_df.set_index(["signal", "geo_value", "time_value"])
            assert merged_df.empty is False
            assert merged_df.value_out.to_numpy() == pytest.approx(merged_df.value_expected, nan_ok=True)

        with self.subTest("diffed signal and smoothed signal in one request"):
            out = self._fetch("/", signal="jhu-csse:confirmed_incidence_num;jhu-csse:confirmed_7dav_incidence_num", geo="county:01", time="day:20200401-20200410")
            out_df = CovidcastRows.from_records(out["epidata"]).api_row_df.set_index(["signal", "geo_value", "time_value"])
            merged_df = pd.merge(out_df, expected_df, left_index=True, right_index=True, suffixes=["_out", "_expected"])[["value_out", "value_expected"]]
            assert merged_df.empty is False
            assert merged_df.value_out.to_numpy() == pytest.approx(merged_df.value_expected, nan_ok=True)

        with self.subTest("smoothing and diffing with a time gap and geo=*"):
            # should fetch 7 extra day to make this work
            out = self._fetch("/", signal="jhu-csse:confirmed_7dav_incidence_num", geo="county:*", time="day:20200407-20200420")
            out_df = CovidcastRows.from_records(out["epidata"]).api_row_df.set_index(["signal", "geo_value", "time_value"])
            merged_df = pd.merge(out_df, expected_df, left_index=True, right_index=True, suffixes=["_out", "_expected"])[["value_out", "value_expected"]]
            assert merged_df.empty is False
            assert merged_df.value_out.to_numpy() == pytest.approx(merged_df.value_expected, nan_ok=True)

        with self.subTest("smoothing and diffing with a time gap and geo=* and time=*"):
            out = self._fetch("/", signal="jhu-csse:confirmed_7dav_incidence_num", geo="county:*", time="day:*")
            out_df = pd.DataFrame.from_records(out["epidata"]).set_index(["signal", "time_value", "geo_value"])
            merged_df = pd.merge(out_df, expected_df, left_index=True, right_index=True, suffixes=["_out", "_expected"])[["value_out", "value_expected"]]
            assert merged_df.empty is False
            assert merged_df.value_out.to_numpy() == pytest.approx(merged_df.value_expected, nan_ok=True)

    def test_compatibility(self):
        """Request at the /api.php endpoint."""
        rows = [CovidcastRow(source="src", signal="sig", time_value=20200401 + i, value=i) for i in range(10)]
        first = rows[0]
        self._insert_rows(rows)

        with self.subTest("simple"):
            out = self._fetch(is_compatibility=True, source=first.source, signal=first.signal, geo=first.geo_pair, time="day:*")
            self.assertEqual(len(out["epidata"]), len(rows))

    def _diff_covidcast_rows(self, rows: List[CovidcastRow]) -> List[CovidcastRow]:
        new_rows = list()
        for x, y in zip(rows[1:], rows[:-1]):
            new_row = copy(x)
            new_row.value = x.value - y.value
            new_rows.append(new_row)
        return new_rows

    def test_trend(self):
        """Request a signal from the /trend endpoint."""

        num_rows = 30
        rows = [CovidcastRow(time_value=20200401 + i, value=i) for i in range(num_rows)]
        first = rows[0]
        last = rows[-1]
        ref = rows[num_rows // 2]
        self._insert_rows(rows)

        with self.subTest("no JIT"):
            out = self._fetch("/trend", signal=first.signal_pair, geo=first.geo_pair, date=last.time_value, window="20200401-20201212", basis=ref.time_value)

            self.assertEqual(out["result"], 1)
            self.assertEqual(len(out["epidata"]), 1)
            trend = out["epidata"][0]
            self.assertEqual(trend["geo_type"], last.geo_type)
            self.assertEqual(trend["geo_value"], last.geo_value)
            self.assertEqual(trend["signal_source"], last.source)
            self.assertEqual(trend["signal_signal"], last.signal)

            self.assertEqual(trend["date"], last.time_value)
            self.assertEqual(trend["value"], last.value)

            self.assertEqual(trend["basis_date"], ref.time_value)
            self.assertEqual(trend["basis_value"], ref.value)
            self.assertEqual(trend["basis_trend"], "increasing")

            self.assertEqual(trend["min_date"], first.time_value)
            self.assertEqual(trend["min_value"], first.value)
            self.assertEqual(trend["min_trend"], "increasing")
            self.assertEqual(trend["max_date"], last.time_value)
            self.assertEqual(trend["max_value"], last.value)
            self.assertEqual(trend["max_trend"], "steady")

        num_rows = 30
        time_value_pairs = [(20200331, 0)] + [(20200401 + i, v) for i, v in enumerate(accumulate(range(num_rows)))]
        rows = [CovidcastRow(source="jhu-csse", signal="confirmed_cumulative_num", time_value=t, value=v) for t, v in time_value_pairs]
        self._insert_rows(rows)
        diffed_rows = self._diff_covidcast_rows(rows)
        for row in diffed_rows:
            row.signal = "confirmed_incidence_num"
        first = diffed_rows[0]
        last = diffed_rows[-1]
        ref = diffed_rows[num_rows // 2]
        with self.subTest("use JIT"):
            out = self._fetch("/trend", signal="jhu-csse:confirmed_incidence_num", geo=first.geo_pair, date=last.time_value, window="20200401-20201212", basis=ref.time_value)

            self.assertEqual(out["result"], 1)
            self.assertEqual(len(out["epidata"]), 1)
            trend = out["epidata"][0]
            self.assertEqual(trend["geo_type"], last.geo_type)
            self.assertEqual(trend["geo_value"], last.geo_value)
            self.assertEqual(trend["signal_source"], last.source)
            self.assertEqual(trend["signal_signal"], last.signal)

            self.assertEqual(trend["date"], last.time_value)
            self.assertEqual(trend["value"], last.value)

            self.assertEqual(trend["basis_date"], ref.time_value)
            self.assertEqual(trend["basis_value"], ref.value)
            self.assertEqual(trend["basis_trend"], "increasing")

            self.assertEqual(trend["min_date"], first.time_value)
            self.assertEqual(trend["min_value"], first.value)
            self.assertEqual(trend["min_trend"], "increasing")
            self.assertEqual(trend["max_date"], last.time_value)
            self.assertEqual(trend["max_value"], last.value)
            self.assertEqual(trend["max_trend"], "steady")


    def test_trendseries(self):
        """Request a signal from the /trendseries endpoint."""

        num_rows = 3
        rows = [CovidcastRow(time_value=20200401 + i, value=num_rows - i) for i in range(num_rows)]
        first = rows[0]
        last = rows[-1]
        self._insert_rows(rows)

        out = self._fetch("/trendseries", signal=first.signal_pair, geo=first.geo_pair, date=last.time_value, window="20200401-20200410", basis=1)

        self.assertEqual(out["result"], 1)
        self.assertEqual(len(out["epidata"]), 3)
        trends = out["epidata"]

        def match_row(trend, row):
            self.assertEqual(trend["geo_type"], row.geo_type)
            self.assertEqual(trend["geo_value"], row.geo_value)
            self.assertEqual(trend["signal_source"], row.source)
            self.assertEqual(trend["signal_signal"], row.signal)

            self.assertEqual(trend["date"], row.time_value)
            self.assertEqual(trend["value"], row.value)

        with self.subTest("trend0"):
            trend = trends[0]
            match_row(trend, first)
            self.assertEqual(trend["basis_date"], None)
            self.assertEqual(trend["basis_value"], None)
            self.assertEqual(trend["basis_trend"], "unknown")

            self.assertEqual(trend["min_date"], last.time_value)
            self.assertEqual(trend["min_value"], last.value)
            self.assertEqual(trend["min_trend"], "increasing")
            self.assertEqual(trend["max_date"], first.time_value)
            self.assertEqual(trend["max_value"], first.value)
            self.assertEqual(trend["max_trend"], "steady")

        with self.subTest("trend1"):
            trend = trends[1]
            match_row(trend, rows[1])
            self.assertEqual(trend["basis_date"], first.time_value)
            self.assertEqual(trend["basis_value"], first.value)
            self.assertEqual(trend["basis_trend"], "decreasing")

            self.assertEqual(trend["min_date"], last.time_value)
            self.assertEqual(trend["min_value"], last.value)
            self.assertEqual(trend["min_trend"], "increasing")
            self.assertEqual(trend["max_date"], first.time_value)
            self.assertEqual(trend["max_value"], first.value)
            self.assertEqual(trend["max_trend"], "decreasing")

        with self.subTest("trend2"):
            trend = trends[2]
            match_row(trend, last)
            self.assertEqual(trend["basis_date"], rows[1].time_value)
            self.assertEqual(trend["basis_value"], rows[1].value)
            self.assertEqual(trend["basis_trend"], "decreasing")

            self.assertEqual(trend["min_date"], last.time_value)
            self.assertEqual(trend["min_value"], last.value)
            self.assertEqual(trend["min_trend"], "steady")
            self.assertEqual(trend["max_date"], first.time_value)
            self.assertEqual(trend["max_value"], first.value)
            self.assertEqual(trend["max_trend"], "decreasing")

        num_rows = 3
        time_value_pairs = [(20200331, 0)] + [(20200401 + i, v) for i, v in enumerate(accumulate([num_rows - i for i in range(num_rows)]))]
        rows = [CovidcastRow(source="jhu-csse", signal="confirmed_cumulative_num", time_value=t, value=v) for t, v in time_value_pairs]
        self._insert_rows(rows)
        diffed_rows = self._diff_covidcast_rows(rows)
        for row in diffed_rows:
            row.signal = "confirmed_incidence_num"
        first = diffed_rows[0]
        last = diffed_rows[-1]

        out = self._fetch("/trendseries", signal="jhu-csse:confirmed_incidence_num", geo=first.geo_pair, date=last.time_value, window="20200401-20200410", basis=1)

        self.assertEqual(out["result"], 1)
        self.assertEqual(len(out["epidata"]), 3)
        trends = out["epidata"]

        with self.subTest("trend0, JIT"):
            trend = trends[0]
            match_row(trend, first)
            self.assertEqual(trend["basis_date"], None)
            self.assertEqual(trend["basis_value"], None)
            self.assertEqual(trend["basis_trend"], "unknown")

            self.assertEqual(trend["min_date"], last.time_value)
            self.assertEqual(trend["min_value"], last.value)
            self.assertEqual(trend["min_trend"], "increasing")
            self.assertEqual(trend["max_date"], first.time_value)
            self.assertEqual(trend["max_value"], first.value)
            self.assertEqual(trend["max_trend"], "steady")

        with self.subTest("trend1"):
            trend = trends[1]
            match_row(trend, diffed_rows[1])
            self.assertEqual(trend["basis_date"], first.time_value)
            self.assertEqual(trend["basis_value"], first.value)
            self.assertEqual(trend["basis_trend"], "decreasing")

            self.assertEqual(trend["min_date"], last.time_value)
            self.assertEqual(trend["min_value"], last.value)
            self.assertEqual(trend["min_trend"], "increasing")
            self.assertEqual(trend["max_date"], first.time_value)
            self.assertEqual(trend["max_value"], first.value)
            self.assertEqual(trend["max_trend"], "decreasing")

        with self.subTest("trend2"):
            trend = trends[2]
            match_row(trend, last)
            self.assertEqual(trend["basis_date"], diffed_rows[1].time_value)
            self.assertEqual(trend["basis_value"], diffed_rows[1].value)
            self.assertEqual(trend["basis_trend"], "decreasing")

            self.assertEqual(trend["min_date"], last.time_value)
            self.assertEqual(trend["min_value"], last.value)
            self.assertEqual(trend["min_trend"], "steady")
            self.assertEqual(trend["max_date"], first.time_value)
            self.assertEqual(trend["max_value"], first.value)
            self.assertEqual(trend["max_trend"], "decreasing")


    def test_correlation(self):
        """Request a signal from the /correlation endpoint."""

        num_rows = 30
        reference_rows = [CovidcastRow(signal="ref", time_value=20200401 + i, value=i) for i in range(num_rows)]
        first = reference_rows[0]
        self._insert_rows(reference_rows)
        other_rows = [CovidcastRow(signal="other", time_value=20200401 + i, value=i) for i in range(num_rows)]
        other = other_rows[0]
        self._insert_rows(other_rows)
        max_lag = 3

        out = self._fetch("/correlation", reference=first.signal_pair, others=other.signal_pair, geo=first.geo_pair, window="20200401-20201212", lag=max_lag)
        self.assertEqual(out["result"], 1)
        df = pd.DataFrame(out["epidata"])
        self.assertEqual(len(df), max_lag * 2 + 1)  # -...0...+
        self.assertEqual(df["geo_type"].unique().tolist(), [first.geo_type])
        self.assertEqual(df["geo_value"].unique().tolist(), [first.geo_value])
        self.assertEqual(df["signal_source"].unique().tolist(), [other.source])
        self.assertEqual(df["signal_signal"].unique().tolist(), [other.signal])

        self.assertEqual(df["lag"].tolist(), list(range(-max_lag, max_lag + 1)))
        self.assertEqual(df["r2"].unique().tolist(), [1.0])
        self.assertEqual(df["slope"].unique().tolist(), [1.0])
        self.assertEqual(df["intercept"].tolist(), [3.0, 2.0, 1.0, 0.0, -1.0, -2.0, -3.0])
        self.assertEqual(df["samples"].tolist(), [num_rows - abs(l) for l in range(-max_lag, max_lag + 1)])

    def test_csv(self):
        """Request a signal from the /csv endpoint."""
        expected_columns = ["geo_value", "signal", "time_value", "issue", "lag", "value", "stderr", "sample_size", "geo_type", "data_source"]
        data = CovidcastRows.from_args(
            time_value=pd.date_range("2020-04-01", "2020-04-10"),
            value=range(10)
        )
        self._insert_rows(data.rows)
        first = data.rows[0]
        with self.subTest("no JIT"):
            response = requests.get(
                f"{BASE_URL}/csv",
                params=dict(signal=first.signal_pair, start_day="2020-04-01", end_day="2020-04-10", geo_type=first.geo_type),
            )
            response.raise_for_status()
            out = response.text
            df = pd.read_csv(StringIO(out), index_col=0)

            self.assertEqual(df.shape, (len(data.rows), 10))
            self.assertEqual(list(df.columns), expected_columns)

        data = CovidcastRows.from_args(
            source=["jhu-csse"] * 10,
            signal=["confirmed_cumulative_num"] * 10,
            time_value=pd.date_range("2020-04-01", "2020-04-10"),
            value=accumulate(range(10)),
        )
        self._insert_rows(data.rows)
        first = data.rows[0]
        with self.subTest("use JIT"):
            # Check that the data loaded correctly.
            response = requests.get(
                f"{BASE_URL}/csv",
                params=dict(signal="jhu-csse:confirmed_cumulative_num", start_day="2020-04-01", end_day="2020-04-10", geo_type=first.geo_type),
            )
            response.raise_for_status()
            df = _read_csv_str(response.text)
            expected_df = data.db_row_df
            compare_cols = ["source", "signal", "time_value", "issue", "lag", "value", "stderr", "sample_size", "geo_type", "geo_value", "time_type"]
            assert_frame_equal_no_order(df[compare_cols], expected_df[compare_cols], index=["source", "signal", "geo_value", "time_value"])

            response = requests.get(
                f"{BASE_URL}/csv",
                params=dict(signal="jhu-csse:confirmed_incidence_num", start_day="2020-04-01", end_day="2020-04-10", geo_type=first.geo_type),
            )
            response.raise_for_status()
            df_diffed = _read_csv_str(response.text)
            expected_df = diff_df(data.db_row_df, "confirmed_incidence_num")
            assert_frame_equal_no_order(df_diffed[compare_cols], expected_df[compare_cols], index=["source", "signal", "geo_value", "time_value"])

    def test_backfill(self):
        """Request a signal from the /backfill endpoint."""

        num_rows = 10
        issue_0 = [CovidcastRow(time_value=20200401 + i, value=i, sample_size=1, lag=0, issue=20200401 + i) for i in range(num_rows)]
        issue_1 = [CovidcastRow(time_value=20200401 + i, value=i + 1, sample_size=2, lag=1, issue=20200401 + i + 1) for i in range(num_rows)]
        last_issue = [CovidcastRow(time_value=20200401 + i, value=i + 2, sample_size=3, lag=2, issue=20200401 + i + 2) for i in range(num_rows)] # <-- the latest issues
        self._insert_rows([*issue_0, *issue_1, *last_issue])
        first = issue_0[0]

        out = self._fetch("/backfill", signal=first.signal_pair, geo=first.geo_pair, time="day:20200401-20201212", anchor_lag=3)
        self.assertEqual(out["result"], 1)
        df = pd.DataFrame(out["epidata"])
        self.assertEqual(len(df), 3 * num_rows)  # num issues
        self.assertEqual(df["time_value"].unique().tolist(), [l.time_value for l in last_issue])

        # check first time point only
        df_t0 = df[df["time_value"] == first.time_value]
        self.assertEqual(len(df_t0), 3)  # num issues
        self.assertEqual(df_t0["issue"].tolist(), [issue_0[0].issue, issue_1[0].issue, last_issue[0].issue])
        self.assertEqual(df_t0["value"].tolist(), [issue_0[0].value, issue_1[0].value, last_issue[0].value])
        self.assertEqual(df_t0["sample_size"].tolist(), [issue_0[0].sample_size, issue_1[0].sample_size, last_issue[0].sample_size])
        self.assertEqual(df_t0["value_rel_change"].astype("str").tolist(), ["nan", "1.0", "1.0"])
        self.assertEqual(df_t0["sample_size_rel_change"].astype("str").tolist(), ["nan", "1.0", "0.5"])  #
        self.assertEqual(df_t0["is_anchor"].tolist(), [False, False, True])
        self.assertEqual(df_t0["value_completeness"].tolist(), [0 / 2, 1 / 2, 2 / 2])  # total 2, given 0,1,2
        self.assertEqual(df_t0["sample_size_completeness"].tolist(), [1 / 3, 2 / 3, 3 / 3])  # total 2, given 0,1,2

    def test_meta(self):
        """Request a signal from the /meta endpoint."""

        num_rows = 10
        rows = [CovidcastRow(time_value=20200401 + i, value=i, source="fb-survey", signal="smoothed_cli") for i in range(num_rows)]
        self._insert_rows(rows)
        first = rows[0]
        last = rows[-1]

        update_cache(args=None)

        with self.subTest("plain"):
            out = self._fetch("/meta")
            self.assertEqual(len(out), 1)
            data_source = out[0]
            self.assertEqual(data_source["source"], first.source)
            self.assertEqual(len(data_source["signals"]), 1)
            stats = data_source["signals"][0]
            self.assertEqual(stats["source"], first.source)
            self.assertEqual(stats["signal"], first.signal)
            self.assertEqual(stats["min_time"], first.time_value)
            self.assertEqual(stats["max_time"], last.time_value)
            self.assertEqual(stats["max_issue"], max(d.issue for d in rows))
            self.assertTrue(first.geo_type in stats["geo_types"])
            stats_g = stats["geo_types"][first.geo_type]
            self.assertEqual(stats_g["min"], first.value)
            self.assertEqual(stats_g["max"], last.value)
            self.assertEqual(stats_g["mean"], sum(r.value for r in rows) / len(rows))

        with self.subTest("filtered"):
            out = self._fetch("/meta", signal=f"{first.source}:*")
            self.assertEqual(len(out), 1)
            data_source = out[0]
            self.assertEqual(data_source["source"], first.source)
            self.assertEqual(len(data_source["signals"]), 1)
            stats = data_source["signals"][0]
            self.assertEqual(stats["source"], first.source)
            out = self._fetch("/meta", signal=f"{first.source}:X")
            self.assertEqual(len(out), 0)

    def test_coverage(self):
        """Request a signal from the /coverage endpoint."""

        num_geos_per_date = [10, 20, 30, 40, 44]
        dates = [20200401 + i for i in range(len(num_geos_per_date))]
        rows = [CovidcastRow(time_value=dates[i], value=i, geo_value=str(geo_value)) for i, num_geo in enumerate(num_geos_per_date) for geo_value in range(num_geo)]
        self._insert_rows(rows)
        first = rows[0]

        with self.subTest("default"):
            out = self._fetch("/coverage", signal=first.signal_pair, geo_type=first.geo_type, latest=dates[-1], format="json")
            self.assertEqual(len(out), len(num_geos_per_date))
            self.assertEqual([o["time_value"] for o in out], dates)
            self.assertEqual([o["count"] for o in out], num_geos_per_date)

        with self.subTest("specify window"):
            out = self._fetch("/coverage", signal=first.signal_pair, geo_type=first.geo_type, window=f"{dates[0]}-{dates[1]}", format="json")
            self.assertEqual(len(out), 2)
            self.assertEqual([o["time_value"] for o in out], dates[:2])
            self.assertEqual([o["count"] for o in out], num_geos_per_date[:2])

        with self.subTest("invalid geo_type"):
            out = self._fetch("/coverage", signal=first.signal_pair, geo_type="doesnt_exist", format="json")
            self.assertEqual(len(out), 0)
