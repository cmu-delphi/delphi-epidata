"""Unit tests for pandas helper."""

# standard library
from dataclasses import dataclass, astuple
from typing import Any, Dict, Iterable
import unittest

import pandas as pd
from sqlalchemy import create_engine

# from flask.testing import FlaskClient
from delphi_utils import Nans
from delphi.epidata.server.main import app
from delphi.epidata.server._pandas import as_pandas
from delphi.epidata.server._query import QueryBuilder

# py3tester coverage target
__test_target__ = "delphi.epidata.server._query"


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
    stderr: float = 0.
    sample_size: float = 10.
    direction_updated_timestamp: int = 20200202
    direction: int = 0
    issue: int = 20200202
    lag: int = 0
    is_latest_issue: bool = True
    is_wip: bool = True
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

    @property
    def astuple(self):
        return astuple(self)[1:]

    @property
    def aslist(self):
        return list(self.astuple)


class UnitTests(unittest.TestCase):
    """Basic unit tests."""

    def setUp(self):
        """Perform per-test setup."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False

        # connect to the `epidata` database and clear the `covidcast` table
        engine = create_engine('mysql://user:pass@delphi_database_epidata/covid')
        cnx = engine.connect()
        cnx.execute("truncate table covidcast")
        cnx.execute('update covidcast_meta_cache set timestamp = 0, epidata = ""')

        # make connection and cursor available to test cases
        self.cnx = cnx

    def tearDown(self):
        """Perform per-test teardown."""
        self.cnx.close()

    def _insert_rows(self, rows: Iterable[CovidcastRow]):
        sql = ",\n".join((str(r) for r in rows))
        self.cnx.execute(
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
        return rows

    def _rows_to_df(self, rows: Iterable[CovidcastRow]) -> pd.DataFrame:
        columns = [
            'id', 'source', 'signal', 'time_type', 'geo_type', 'time_value',
            'geo_value', 'value_updated_timestamp', 'value', 'stderr',
            'sample_size', 'direction_updated_timestamp', 'direction', 'issue',
            'lag', 'is_latest_issue', 'is_wip', 'missing_value', 'missing_stderr',
            'missing_sample_size'
        ]
        return pd.DataFrame.from_records([[i] + row.aslist for i, row in enumerate(rows, start=1)], columns=columns)

    def test_as_pandas(self):
        rows = [CovidcastRow(time_value=20200401 + i, value=float(i)) for i in range(10)]
        self._insert_rows(rows)

        with app.test_request_context('/correlation'):
            q = QueryBuilder("covidcast", "t")

            df = as_pandas(str(q), params={}, db_engine=self.cnx, parse_dates=None).astype({"is_latest_issue": bool, "is_wip": bool})
            expected_df = self._rows_to_df(rows)
            pd.testing.assert_frame_equal(df, expected_df)
            df = as_pandas(str(q), params={}, db_engine=self.cnx, parse_dates=None, limit_rows=5).astype({"is_latest_issue": bool, "is_wip": bool})
            expected_df = self._rows_to_df(rows[:5])
            pd.testing.assert_frame_equal(df, expected_df)
