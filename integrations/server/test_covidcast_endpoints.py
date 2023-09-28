"""Integration tests for the custom `covidcast/*` endpoints."""

# standard library
from io import StringIO
from typing import Sequence

# third party
from more_itertools import windowed
import pandas as pd

from delphi.epidata.maintenance.covidcast_meta_cache_updater import main as update_cache
from delphi.epidata.common.covidcast_test_base import CovidcastTestBase, CovidcastTestRow


class CovidcastEndpointTests(CovidcastTestBase):
    """Tests the `covidcast/*` endpoint."""

    def localSetUp(self):
        """Perform per-test setup."""
        self.role_name = "quidel"

    def _diff_rows(self, rows: Sequence[float]):
        return [
            float(x - y) if x is not None and y is not None else None
            for x, y in zip(rows[1:], rows[:-1])
        ]

    def _smooth_rows(self, rows: Sequence[float]):
        return [
            sum(e)/len(e) if None not in e else None 
            for e in windowed(rows, 7)
        ]

    def test_basic(self):
        """Request a signal from the / endpoint."""
        rows = [CovidcastTestRow.make_default_row(time_value=2020_04_01 + i, value=i) for i in range(10)]
        first = rows[0]
        self._insert_rows(rows)

        with self.subTest("validation"):
            out = self._make_request(auth=self.epidata_client.auth, json=True, raise_for_status=True)
            self.assertEqual(out["result"], -1)

        with self.subTest("simple"):
            params = {
                "signal": first.signal_pair(),
                "geo": first.geo_pair(),
                "time": "day:*"
            }
            out = self._make_request(auth=self.epidata_client.auth, json=True, raise_for_status=True, params=params)
            self.assertEqual(len(out["epidata"]), len(rows))

    def test_basic_restricted_source(self):
        """Request a signal from the / endpoint."""
        rows = [CovidcastTestRow.make_default_row(time_value=2020_04_01 + i, value=i, source="quidel") for i in range(10)]
        first = rows[0]
        self._insert_rows(rows)

        with self.subTest("validation"):
            out = self._make_request(auth=self.epidata_client.auth, json=True, raise_for_status=True)
            self.assertEqual(out["result"], -1)

        with self.subTest("no_roles"):
            params = {
                "signal": first.signal_pair(),
                "geo": first.geo_pair(),
                "time": "day:*"
            }
            out = self._make_request(auth=self.epidata_client.auth, json=True, raise_for_status=True, params=params)
            self.assertEqual(len(out["epidata"]), 0)

        with self.subTest("no_api_key"):
            params = {
                "signal": first.signal_pair(),
                "geo": first.geo_pair(),
                "time": "day:*"
            }
            out = self._make_request(json=True, raise_for_status=True, params=params)
            self.assertEqual(len(out["epidata"]), 0)

        with self.subTest("quidel_role"):
            params = {
                "signal": first.signal_pair(),
                "geo": first.geo_pair(),
                "time": "day:*",
                "auth": "quidel_key"
            }
            out = self._make_request(json=True, raise_for_status=True, params=params)
            self.assertEqual(len(out["epidata"]), len(rows))

    # Commented out this section as we want go get rid of legacy .php code
    # -----------------------------------------
    # def test_compatibility(self):
    #     """Request at the /api.php endpoint."""
    #     rows = [CovidcastTestRow.make_default_row(source="src", signal="sig", time_value=2020_04_01 + i, value=i) for i in range(10)]
    #     first = rows[0]
    #     self._insert_rows(rows)

    #     with self.subTest("validation"):
    #         out = self._fetch("/", is_compatibility=True)
    #         self.assertEqual(out["result"], -1)

    #     with self.subTest("simple"):
    #         out = self._fetch("/", signal=first.signal_pair(), geo=first.geo_pair(), time="day:*", is_compatibility=True)
    #         self.assertEqual(out["epidata"], [row.as_api_compatibility_row_dict() for row in rows])

    # def test_compatibility_restricted_source(self):
    #     """Restricted request at the /api.php endpoint."""
    #     rows = [CovidcastTestRow.make_default_row(time_value=2020_04_01 + i, value=i, source="quidel") for i in range(10)]
    #     first = rows[0]
    #     self._insert_rows(rows)

    #     with self.subTest("no_roles"):
    #         out = self._fetch("/", signal=first.signal_pair(), geo=first.geo_pair(), time="day:*", is_compatibility=True)
    #         self.assertTrue("epidata" not in out)

    #     with self.subTest("no_api_key"):
    #         out = self._fetch("/", auth=None, signal=first.signal_pair(), geo=first.geo_pair(), time="day:*", is_compatibility=True)
    #         self.assertTrue("epidata" not in out)

    #     with self.subTest("quidel_role"):
    #         out = self._fetch("/", auth=("epidata", "quidel_key"), signal=first.signal_pair(), geo=first.geo_pair(), time="day:*", is_compatibility=True)
    #         self.assertEqual(out["epidata"], [row.as_api_compatibility_row_dict() for row in rows])
    # -----------------------------------------

    def test_trend(self):
        """Request a signal from the /trend endpoint."""

        num_rows = 30
        rows = [CovidcastTestRow.make_default_row(time_value=2020_04_01 + i, value=i) for i in range(num_rows)]
        first = rows[0]
        last = rows[-1]
        ref = rows[num_rows // 2]
        self._insert_rows(rows)

        params = {
            "signal": first.signal_pair(),
            "geo": first.geo_pair(),
            "date": last.time_value,
            "window": "20200401-20201212",
            "basis": ref.time_value
        }
        out = self._make_request(endpoint="covidcast/trend", auth=self.epidata_client.auth, json=True, raise_for_status=True, params=params)

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
        rows = [CovidcastTestRow.make_default_row(time_value=2020_04_01 + i, value=num_rows - i) for i in range(num_rows)]
        first = rows[0]
        last = rows[-1]
        self._insert_rows(rows)

        params = {
            "signal": first.signal_pair(),
            "geo": first.geo_pair(),
            "date": last.time_value,
            "window": "20200401-20200410",
            "basis": 1
        }
        out = self._make_request(endpoint="covidcast/trendseries", auth=self.epidata_client.auth, json=True, raise_for_status=True, params=params)

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

    def test_csv(self):
        """Request a signal from the /csv endpoint."""

        rows = [CovidcastTestRow.make_default_row(time_value=2020_04_01 + i, value=i) for i in range(10)]
        first = rows[0]
        self._insert_rows(rows)

        params = {
            "signal": first.signal_pair(),
            "start_day": "2020-04-01",
            "end_day": "2020-12-12",
            "geo_type": first.geo_type
        }
        response = self._make_request(endpoint="covidcast/csv", raise_for_status=True, params=params)
        out = response.text
        df = pd.read_csv(StringIO(out), index_col=0)
        self.assertEqual(df.shape, (len(rows), 10))
        self.assertEqual(list(df.columns), ["geo_value", "signal", "time_value", "issue", "lag", "value", "stderr", "sample_size", "geo_type", "data_source"])

    def test_backfill(self):
        """Request a signal from the /backfill endpoint."""

        TEST_DATE_VALUE = 2020_04_01
        num_rows = 10
        issue_0 = [CovidcastTestRow.make_default_row(time_value=TEST_DATE_VALUE + i, value=i, sample_size=1, lag=0, issue=TEST_DATE_VALUE + i) for i in range(num_rows)]
        issue_1 = [CovidcastTestRow.make_default_row(time_value=TEST_DATE_VALUE + i, value=i + 1, sample_size=2, lag=1, issue=TEST_DATE_VALUE + i + 1) for i in range(num_rows)]
        last_issue = [CovidcastTestRow.make_default_row(time_value=TEST_DATE_VALUE + i, value=i + 2, sample_size=3, lag=2, issue=TEST_DATE_VALUE + i + 2) for i in range(num_rows)] # <-- the latest issues
        self._insert_rows([*issue_0, *issue_1, *last_issue])
        first = issue_0[0]

        params = {
            "signal": first.signal_pair(),
            "geo": first.geo_pair(),
            "time": "day:20200401-20201212",
            "anchor_lag": 3
        }
        out = self._make_request(endpoint="covidcast/backfill", auth=self.epidata_client.auth, json=True, raise_for_status=True, params=params)
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
        rows = [CovidcastTestRow.make_default_row(time_value=2020_04_01 + i, value=i, source="fb-survey", signal="smoothed_cli") for i in range(num_rows)]
        self._insert_rows(rows)
        first = rows[0]
        last = rows[-1]

        update_cache(args=None)

        with self.subTest("plain"):
            out = self._make_request(endpoint="covidcast/meta", auth=self.epidata_client.auth, json=True, raise_for_status=True)
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
            params = {
                "signal": f"{first.source}:*"
            }
            out = self._make_request(endpoint="covidcast/meta", auth=self.epidata_client.auth, json=True, raise_for_status=True, params=params)
            self.assertEqual(len(out), 1)
            data_source = out[0]
            self.assertEqual(data_source["source"], first.source)
            self.assertEqual(len(data_source["signals"]), 1)
            stats = data_source["signals"][0]
            self.assertEqual(stats["source"], first.source)
            params = {
                "signal": f"{first.source}:X"
            }
            out = self._make_request(endpoint="covidcast/meta", auth=self.epidata_client.auth, json=True, raise_for_status=True, params=params)
            self.assertEqual(len(out), 0)

    def test_meta_restricted(self):
        """Request 'restricted' signals from the /meta endpoint."""
        # NOTE: this method is nearly identical to ./test_covidcast_meta.py:test_restricted_sources()
        #       ...except the self._make_request() methods are different, as is the format of those methods' outputs
        #       (the other covidcast_meta endpoint uses APrinter, this one returns its own unadulterated json).
        #       additionally, the sample data used here must match entries (that is, named sources and signals)
        #       from covidcast_utils.model.data_sources (the `data_sources` variable from file
        #       src/server/endpoints/covidcast_utils/model.py, which is created by the _load_data_sources() method
        #       and fed by src/server/endpoints/covidcast_utils/db_sources.csv, but also surreptitiously augmened
        #       by _load_data_signals() which attaches a list of signals to each source,
        #       in turn fed by src/server/endpoints/covidcast_utils/db_signals.csv)

        # insert data from two different sources, one restricted/protected (quidel), one not
        self._insert_rows([
            CovidcastTestRow.make_default_row(source="quidel", signal="raw_pct_negative"),
            CovidcastTestRow.make_default_row(source="hhs", signal="confirmed_admissions_covid_1d")
        ])

        # update metadata cache
        update_cache(args=None)

        # verify unauthenticated (no api key) or unauthorized (user w/o privilege) only see metadata for one source
        unauthenticated_request = self._make_request(endpoint="covidcast/meta", json=True, raise_for_status=True)
        unauthorized_request = self._make_request(endpoint="covidcast/meta", auth=self.epidata_client.auth, json=True, raise_for_status=True)
        self.assertEqual(len(unauthenticated_request), 1)
        self.assertEqual(len(unauthorized_request), 1)

        # verify authorized user sees metadata for both sources
        qauth = ('epidata', 'quidel_key')
        authorized_request = self._make_request(endpoint="covidcast/meta", auth=qauth, json=True, raise_for_status=True)
        self.assertEqual(len(authorized_request), 2)

    def test_coverage(self):
        """Request a signal from the /coverage endpoint."""

        num_geos_per_date = [10, 20, 30, 40, 44]
        dates = [2020_04_01 + i for i in range(len(num_geos_per_date))]
        rows = [CovidcastTestRow.make_default_row(time_value=dates[i], value=i, geo_value=str(geo_value)) for i, num_geo in enumerate(num_geos_per_date) for geo_value in range(num_geo)]
        self._insert_rows(rows)
        first = rows[0]

        with self.subTest("default"):
            params = {
                "signal": first.signal_pair(),
                "geo_type": first.geo_type,
                "latest": dates[-1],
                "format": "json"
            }
            out = self._make_request(endpoint="covidcast/coverage", auth=self.epidata_client.auth, json=True, raise_for_status=True, params=params)
            self.assertEqual(len(out), len(num_geos_per_date))
            self.assertEqual([o["time_value"] for o in out], dates)
            self.assertEqual([o["count"] for o in out], num_geos_per_date)

        with self.subTest("specify window"):
            params = {
                "signal": first.signal_pair(),
                "geo_type": first.geo_type,
                "window": f"{dates[0]}-{dates[1]}",
                "format": "json"
            }
            out = self._make_request("covidcast/coverage", auth=self.epidata_client.auth, json=True, raise_for_status=True, params=params)
            self.assertEqual(len(out), 2)
            self.assertEqual([o["time_value"] for o in out], dates[:2])
            self.assertEqual([o["count"] for o in out], num_geos_per_date[:2])

        with self.subTest("invalid geo_type"):
            params = {
                "signal": first.signal_pair(),
                "geo_type": "doesnt_exist",
                "format": "json"
            }
            out = self._make_request(endpoint="covidcast/coverage", auth=self.epidata_client.auth, json=True, raise_for_status=True, params=params)
            self.assertEqual(len(out), 0)
