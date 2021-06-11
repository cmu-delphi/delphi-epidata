"""Integration tests for the custom `covidcast/*` endpoints."""

# standard library
from typing import Iterable, Dict, Any
import unittest
from io import StringIO

# from typing import Optional
from dataclasses import dataclass

# third party
import mysql.connector
import requests
import pandas as pd
from delphi_utils import Nans

from delphi.epidata.acquisition.covidcast.covidcast_meta_cache_updater import main as update_cache


# use the local instance of the Epidata API
BASE_URL = "http://delphi_web_epidata/epidata/covidcast"


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
            insert into covidcast values
            {sql}
            """
        )
        self.cnx.commit()
        return rows

    def _fetch(self, endpoint="/", **params):
        # make the request
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            params=params,
        )
        response.raise_for_status()
        return response.json()

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

    def test_trend(self):
        """Request a signal the /trend endpoint."""

        num_rows = 30
        rows = [CovidcastRow(time_value=20200401 + i, value=i) for i in range(num_rows)]
        first = rows[0]
        last = rows[-1]
        ref = rows[num_rows // 2]
        self._insert_rows(rows)

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

        rows = [CovidcastRow(time_value=20200401 + i, value=i) for i in range(10)]
        first = rows[0]
        self._insert_rows(rows)

        response = requests.get(
            f"{BASE_URL}/csv",
            params=dict(signal=first.signal_pair, start_day="2020-04-01", end_day="2020-12-12", geo_type=first.geo_type),
        )
        response.raise_for_status()
        out = response.text
        df = pd.read_csv(StringIO(out), index_col=0)
        self.assertEqual(df.shape, (len(rows), 10))
        self.assertEqual(list(df.columns), ["geo_value", "signal", "time_value", "issue", "lag", "value", "stderr", "sample_size", "geo_type", "data_source"])

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
        rows = [CovidcastRow(time_value=20200401 + i, value=i) for i in range(num_rows)]
        self._insert_rows(rows)
        first = rows[0]
        last = rows[-1]

        update_cache(args=None)

        with self.subTest("plain"):
            out = self._fetch("/meta")
            self.assertEqual(len(out), 1)
            stats = out[0]
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
            self.assertEqual(out[0]["source"], first.source)
            out = self._fetch("/meta", signal=f"{first.source}:X")
            self.assertEqual(len(out), 0)

    def test_coverage(self):
        """Request a signal the /meta endpoint."""

        num_geos_per_date = [10, 20, 30, 40, 44]
        dates = [20200401 + i for i in range(num_geos_per_date)]
        rows = [CovidcastRow(time_value=dates[i], value=i, geo_value=str(geo_value)) for i, num_geo in enumerate(num_geos_per_date) for geo_value in range(num_geo)]
        self._insert_rows(rows)

        with self.subTest("default"):
            out = self._fetch("/coverage")
            self.assertEqual(len(out), len(num_geos_per_date))
            self.assertEqual([o["time_value"] for o in out], dates)
            self.assertEqual([o["count"] for o in out], num_geos_per_date)

        with self.subTest("specify window"):
            out = self._fetch("/coverage", window="20200401-20200402")
            self.assertEqual(len(out), 2)
            self.assertEqual([o["time_value"] for o in out], dates[:2])
            self.assertEqual([o["count"] for o in out], num_geos_per_date[:2])
        with self.subTest("invalid geo_type"):
            out = self._fetch("/coverage", geo_type="state")
            self.assertEqual(len(out), 0)
