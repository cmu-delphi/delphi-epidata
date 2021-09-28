"""Integration tests for the custom `covidcast/*` endpoints."""

# standard library
from copy import copy
from itertools import accumulate, chain
from typing import Iterable, Dict, Any, List, Sequence
import unittest
from io import StringIO

# from typing import Optional
from dataclasses import dataclass

# third party
import mysql.connector
from more_itertools import interleave_longest, windowed
import requests
import pandas as pd
import numpy as np
from delphi_utils import Nans

from delphi.epidata.acquisition.covidcast.covidcast_meta_cache_updater import main as update_cache
from delphi.epidata.server.endpoints.covidcast_utils.model import DataSignal, DataSource


# use the local instance of the Epidata API
BASE_URL = "http://delphi_web_epidata/epidata/covidcast"
BASE_URL_OLD = "http://delphi_web_epidata/epidata/api.php"


@dataclass
class CovidcastRow:
    id: int = 0
    source: str = "src"
    signal: str = "sig"
    time_type: str = "day"
    geo_type: str = "county"
    time_value: int = 20200411
    geo_value: str = "01234"
    value_updated_timestamp: int = 20200202
    value: float = 10.0
    stderr: float = 0
    sample_size: float = 10
    direction_updated_timestamp: int = 20200202
    direction: int = 0
    issue: int = 20200202
    lag: int = 0
    is_latest_issue: bool = True
    is_wip: bool = False
    missing_value: int = Nans.NOT_MISSING
    missing_stderr: int = Nans.NOT_MISSING
    missing_sample_size: int = Nans.NOT_MISSING

    def __str__(self):
        return f"""(
            {self.id},
            '{self.source}',
            '{self.signal}',
            '{self.time_type}',
            '{self.geo_type}',
            {self.time_value},
            '{self.geo_value}',
            {self.value_updated_timestamp},
            {self.value},
            {self.stderr},
            {self.sample_size},
            {self.direction_updated_timestamp},
            {self.direction},
            {self.issue},
            {self.lag},
            {self.is_latest_issue},
            {self.is_wip},
            {self.missing_value},
            {self.missing_stderr},
            {self.missing_sample_size}
            )"""

    @staticmethod
    def from_json(json: Dict[str, Any]) -> "CovidcastRow":
        return CovidcastRow(
            source=json["source"],
            signal=json["signal"],
            time_type=json["time_type"],
            geo_type=json["geo_type"],
            geo_value=json["geo_value"],
            direction=json["direction"],
            issue=json["issue"],
            lag=json["lag"],
            value=json["value"],
            stderr=json["stderr"],
            sample_size=json["sample_size"],
            missing_value=json["missing_value"],
            missing_stderr=json["missing_stderr"],
            missing_sample_size=json["missing_sample_size"],
        )

    @property
    def signal_pair(self):
        return f"{self.source}:{self.signal}"

    @property
    def geo_pair(self):
        return f"{self.geo_type}:{self.geo_value}"

    @property
    def time_pair(self):
        return f"{self.time_type}:{self.time_value}"


class CovidcastEndpointTests(unittest.TestCase):
    """Tests the `covidcast/*` endpoint."""

    def setUp(self):
        """Perform per-test setup."""

        # connect to the `epidata` database and clear the `covidcast` table
        cnx = mysql.connector.connect(user="user", password="pass", host="delphi_database_epidata", database="epidata")
        cur = cnx.cursor()
        cur.execute("truncate table covidcast")
        cur.execute('update covidcast_meta_cache set timestamp = 0, epidata = ""')
        cnx.commit()
        cur.close()

        # make connection and cursor available to test cases
        self.cnx = cnx
        self.cur = cnx.cursor()

    def tearDown(self):
        """Perform per-test teardown."""
        self.cur.close()
        self.cnx.close()

    def _insert_rows(self, rows: Iterable[CovidcastRow]):
        sql = ",\n".join((str(r) for r in rows))
        self.cur.execute(
            f"""
            INSERT INTO
                `covidcast` (`id`, `source`, `signal`, `time_type`, `geo_type`,
	            `time_value`, `geo_value`, `value_updated_timestamp`,
                `value`, `stderr`, `sample_size`, `direction_updated_timestamp`,
                `direction`, `issue`, `lag`, `is_latest_issue`, `is_wip`,`missing_value`,
                `missing_stderr`,`missing_sample_size`)
            VALUES
            {sql}
            """
        )
        self.cnx.commit()
        return rows

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

    def _diff_rows(self, rows: Sequence[float]):
        return [float(x - y) if x is not None and y is not None else None for x, y in zip(rows[1:], rows[:-1])]

    def _smooth_rows(self, rows: Sequence[float]):
        return [sum(e)/len(e) if None not in e else None for e in windowed(rows, 7)]

    def test_basic(self):
        """Request a signal the / endpoint."""

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
            self.assertEqual(len(out["epidata"]), len(rows))
            out_values = [row["value"] for row in out["epidata"]]
            expected_values = [float(row.value) for row in rows]
            self.assertEqual(out_values, expected_values)

    def test_derived_signals(self):
        time_value_pairs = [(20200401 + i, i ** 2) for i in range(10)]
        rows01 = [CovidcastRow(source="jhu-csse", signal="confirmed_cumulative_num", time_value=time_value, value=value, geo_value="01") for time_value, value in time_value_pairs]
        rows02 = [CovidcastRow(source="jhu-csse", signal="confirmed_cumulative_num", time_value=time_value, value=2 * value, geo_value="02") for time_value, value in time_value_pairs]
        first = rows01[0]
        self._insert_rows(rows01 + rows02)

        with self.subTest("diffed signal"):
            out = self._fetch("/", signal="jhu-csse:confirmed_incidence_num", geo=first.geo_pair, time="day:*")
            assert out['result'] == -2
            out = self._fetch("/", signal="jhu-csse:confirmed_incidence_num", geo=first.geo_pair, time="day:20200401-20200410")
            self.assertEqual(len(out["epidata"]), len(rows01))
            out_values = [row["value"] for row in out["epidata"]]
            values = [None] + [value for _, value in time_value_pairs]
            expected_values = self._diff_rows(values)
            self.assertAlmostEqual(out_values, expected_values)

        with self.subTest("diffed signal, multiple geos"):
            out = self._fetch("/", signal="jhu-csse:confirmed_incidence_num", geo="county:01,02", time="day:20200401-20200410")
            self.assertEqual(len(out["epidata"]), 2*(len(rows01)))
            out_values = [row["value"] for row in out["epidata"]]
            values1 = [None] + [value for _, value in time_value_pairs]
            values2 = [None] + [2 * value for _, value in time_value_pairs]
            expected_values = self._diff_rows(values1) + self._diff_rows(values2)
            self.assertAlmostEqual(out_values, expected_values)

        with self.subTest("diffed signal, multiple geos using geo:*"):
            out = self._fetch("/", signal="jhu-csse:confirmed_incidence_num", geo="county:*", time="day:20200401-20200410")
            self.assertEqual(len(out["epidata"]), 2*(len(rows01)))
            values1 = [None] + [value for _, value in time_value_pairs]
            values2 = [None] + [2 * value for _, value in time_value_pairs]
            expected_values = self._diff_rows(values1) + self._diff_rows(values2)
            self.assertAlmostEqual(out_values, expected_values)

        with self.subTest("smoothed signal"):
            out = self._fetch("/", signal="jhu-csse:confirmed_7dav_incidence_num", geo=first.geo_pair, time="day:20200401-20200410")
            self.assertEqual(len(out["epidata"]), len(rows01))
            out_values = [row["value"] for row in out["epidata"]]
            values = [None] * 7 + [value for _, value in time_value_pairs]
            expected_values = self._smooth_rows(self._diff_rows(values))
            self.assertAlmostEqual(out_values, expected_values)

        with self.subTest("diffed signal and smoothed signal in one request"):
            out = self._fetch("/", signal="jhu-csse:confirmed_incidence_num;jhu-csse:confirmed_7dav_incidence_num", geo=first.geo_pair, time="day:20200401-20200410")
            self.assertEqual(len(out["epidata"]), 2*len(rows01) + 6)
            out_values = [row["value"] for row in out["epidata"]]
            values = [None] * 7 + [value for _, value in time_value_pairs]
            expected_diff = self._diff_rows(values)
            expected_smoothed = self._smooth_rows(expected_diff)
            expected_values = list(interleave_longest(expected_smoothed, expected_diff))
            self.assertAlmostEqual(out_values, expected_values)

        with self.subTest("smoothing with time window resizing"):
            # should fetch 6 extra days
            out = self._fetch("/", signal="jhu-csse:confirmed_7dav_incidence_num", geo=first.geo_pair, time="day:20200407-20200410")
            self.assertEqual(len(out["epidata"]), len(rows01) - 6)
            out_values = [row["value"] for row in out["epidata"]]
            # an extra None is added because the padding for DIFF_SMOOTH (pad_length = 8) is used
            values = [None] + [value for _, value in time_value_pairs]
            expected_values = self._smooth_rows(self._diff_rows(values))
            self.assertAlmostEqual(out_values, expected_values)

        with self.subTest("diffing with time window resizing"):
            # should fetch 1 extra day
            out = self._fetch("/", signal="jhu-csse:confirmed_incidence_num", geo=first.geo_pair, time="day:20200402-20200410")
            self.assertEqual(len(out["epidata"]), len(rows01) - 1)
            out_values = [row["value"] for row in out["epidata"]]
            values = [value for _, value in time_value_pairs]
            expected_values = self._diff_rows(values)
            self.assertAlmostEqual(out_values, expected_values)

        time_value_pairs = [(20200401 + i, i ** 2) for i in chain(range(10), range(15, 20))]
        rows = [CovidcastRow(source="jhu-csse", signal="confirmed_cumulative_num", geo_value="03", time_value=time_value, value=value) for time_value, value in time_value_pairs]
        first = rows[0]
        self._insert_rows(rows)

        with self.subTest("smoothing with a time gap"):
            # should fetch 1 extra day
            out = self._fetch("/", signal="jhu-csse:confirmed_7dav_incidence_num", geo=first.geo_pair, time="day:20200401-20200420")
            self.assertEqual(len(out["epidata"]), len(rows) + 5)
            out_values = [row["value"] for row in out["epidata"]]
            values = [None] * 7 + [value for _, value in time_value_pairs][:10] + [None] * 5 + [value for _, value in time_value_pairs][10:]
            expected_values = self._smooth_rows(self._diff_rows(values))
            self.assertAlmostEqual(out_values, expected_values)

        with self.subTest("diffing with a time gap"):
            # should fetch 1 extra day
            out = self._fetch("/", signal="jhu-csse:confirmed_incidence_num", geo=first.geo_pair, time="day:20200401-20200420")
            self.assertEqual(len(out["epidata"]), len(rows) + 5)
            out_values = [row["value"] for row in out["epidata"]]
            values = [None] + [value for _, value in time_value_pairs][:10] + [None] * 5 + [value for _, value in time_value_pairs][10:]
            expected_values = self._diff_rows(values)
            self.assertAlmostEqual(out_values, expected_values)


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
        """Request a signal the /trend endpoint."""

        num_rows = 30
        rows = [CovidcastRow(time_value=20200401 + i, value=i) for i in range(num_rows)]
        first = rows[0]
        last = rows[-1]
        ref = rows[num_rows // 2]
        self._insert_rows(rows)

        with self.subTest("no server-side compute"):
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
        with self.subTest("use server-side compute"):
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
        """Request a signal the /trendseries endpoint."""

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

        with self.subTest("trend0, server-side compute"):
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
        """Request a signal the /correlation endpoint."""

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
        """Request a signal the /csv endpoint."""

        expected_columns = ["geo_value", "signal", "time_value", "issue", "lag", "value", "stderr", "sample_size", "geo_type", "data_source"]
        rows = [CovidcastRow(time_value=20200401 + i, value=i) for i in range(10)]
        self._insert_rows(rows)
        first = rows[0]
        with self.subTest("no server-side compute"):
            response = requests.get(
                f"{BASE_URL}/csv",
                params=dict(signal=first.signal_pair, start_day="2020-04-01", end_day="2020-04-10", geo_type=first.geo_type),
            )
            response.raise_for_status()
            out = response.text
            df = pd.read_csv(StringIO(out), index_col=0)

            self.assertEqual(df.shape, (len(rows), 10))
            self.assertEqual(list(df.columns), expected_columns)

        num_rows = 10
        time_value_pairs = [(20200331, 0)] + [(20200401 + i, v) for i, v in enumerate(accumulate(range(num_rows)))]
        rows = [CovidcastRow(source="jhu-csse", signal="confirmed_cumulative_num", time_value=t, value=v) for t, v in time_value_pairs]
        self._insert_rows(rows)
        first = rows[0]
        with self.subTest("use server-side compute"):
            response = requests.get(
                f"{BASE_URL}/csv",
                params=dict(signal="src:sig", start_day="2020-04-01", end_day="2020-04-10", geo_type=first.geo_type),
            )
            response.raise_for_status()
            out = response.text
            df = pd.read_csv(StringIO(out), index_col=0)
            df.stderr = np.nan
            df.sample_size = np.nan

            response = requests.get(
                f"{BASE_URL}/csv",
                params=dict(signal="jhu-csse:confirmed_incidence_num", start_day="2020-04-01", end_day="2020-04-10", geo_type=first.geo_type),
            )
            response.raise_for_status()
            out = response.text
            df_diffed = pd.read_csv(StringIO(out), index_col=0)
            df_diffed.signal = "sig"
            df_diffed.data_source = "src"

            self.assertEqual(df_diffed.shape, (num_rows, 10))
            self.assertEqual(list(df_diffed.columns), expected_columns)
            pd.testing.assert_frame_equal(df_diffed, df)

    def test_backfill(self):
        """Request a signal the /backfill endpoint."""

        num_rows = 10
        issue_0 = [CovidcastRow(time_value=20200401 + i, value=i, sample_size=1, lag=0, issue=20200401 + i, is_latest_issue=False) for i in range(num_rows)]
        issue_1 = [CovidcastRow(time_value=20200401 + i, value=i + 1, sample_size=2, lag=1, issue=20200401 + i + 1, is_latest_issue=False) for i in range(num_rows)]
        last_issue = [CovidcastRow(time_value=20200401 + i, value=i + 2, sample_size=3, lag=2, issue=20200401 + i + 2, is_latest_issue=True) for i in range(num_rows)]
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
        """Request a signal the /meta endpoint."""

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
        """Request a signal the /coverage endpoint."""

        num_geos_per_date = [10, 20, 30, 40, 44]
        dates = [20200401 + i for i in range(len(num_geos_per_date))]
        rows = [CovidcastRow(time_value=dates[i], value=i, geo_value=str(geo_value)) for i, num_geo in enumerate(num_geos_per_date) for geo_value in range(num_geo)]
        self._insert_rows(rows)
        first = rows[0]

        with self.subTest("default"):
            out = self._fetch("/coverage", signal=first.signal_pair, latest=dates[-1], format="json")
            self.assertEqual(len(out), len(num_geos_per_date))
            self.assertEqual([o["time_value"] for o in out], dates)
            self.assertEqual([o["count"] for o in out], num_geos_per_date)

        with self.subTest("specify window"):
            out = self._fetch("/coverage", signal=first.signal_pair, window=f"{dates[0]}-{dates[1]}", format="json")
            self.assertEqual(len(out), 2)
            self.assertEqual([o["time_value"] for o in out], dates[:2])
            self.assertEqual([o["count"] for o in out], num_geos_per_date[:2])

        with self.subTest("invalid geo_type"):
            out = self._fetch("/coverage", signal=first.signal_pair, geo_type="state", format="json")
            self.assertEqual(len(out), 0)
