import unittest
from dataclasses import fields
from datetime import date
from typing import Any, Dict, Iterable, List, Optional, Sequence

import delphi.operations.secrets as secrets
import pandas as pd
from delphi.epidata.acquisition.covidcast.covidcast_row import CovidcastRow
from delphi.epidata.acquisition.covidcast.database import Database
from delphi.epidata.server.utils.dates import day_to_time_value, time_value_to_day
from delphi_utils import Nans

# all the Nans we use here are just one value, so this is a shortcut to it:
nmv = Nans.NOT_MISSING.value


class CovidcastTestRow(CovidcastRow):
    @staticmethod
    def make_default_row(**kwargs) -> "CovidcastTestRow":
        default_args = {
            "source": "src",
            "signal": "sig",
            "time_type": "day",
            "geo_type": "county",
            "time_value": 2020_02_02,
            "geo_value": "01234",
            "value": 10.0,
            "stderr": 10.0,
            "sample_size": 10.0,
            "missing_value": Nans.NOT_MISSING.value,
            "missing_stderr": Nans.NOT_MISSING.value,
            "missing_sample_size": Nans.NOT_MISSING.value,
            "issue": 2020_02_02,
            "lag": 0,
        }
        default_args.update(kwargs)
        return CovidcastTestRow(**default_args)

    def __post_init__(self):
        # Convert time values to ints by default.
        if isinstance(self.time_value, date):
            self.time_value = day_to_time_value(self.time_value)
        if isinstance(self.issue, date):
            self.issue = day_to_time_value(self.issue)
        if isinstance(self.value_updated_timestamp, date):
            self.value_updated_timestamp = day_to_time_value(self.value_updated_timestamp)

    def _sanitize_fields(self, extra_checks: bool = True):
        if self.issue and self.issue < self.time_value:
            self.issue = self.time_value

        if self.issue:
            self.lag = (time_value_to_day(self.issue) - time_value_to_day(self.time_value)).days
        else:
            self.lag = None

        # This sanity checking is already done in CsvImporter, but it's here so the testing class gets it too.
        if pd.isna(self.value) and self.missing_value == Nans.NOT_MISSING:
            self.missing_value = Nans.NOT_APPLICABLE.value if extra_checks else Nans.OTHER.value

        if pd.isna(self.stderr) and self.missing_stderr == Nans.NOT_MISSING:
            self.missing_stderr = Nans.NOT_APPLICABLE.value if extra_checks else Nans.OTHER.value

        if pd.isna(self.sample_size) and self.missing_sample_size == Nans.NOT_MISSING:
            self.missing_sample_size = Nans.NOT_APPLICABLE.value if extra_checks else Nans.OTHER.value

        return self


def covidcast_rows_from_args(sanitize_fields: bool = False, test_mode: bool = True, **kwargs: Dict[str, Iterable]) -> List[CovidcastTestRow]:
    """A convenience constructor for test rows.

    Example:
    covidcast_rows_from_args(value=[1, 2, 3], time_value=[1, 2, 3]) will yield
    [CovidcastTestRow.make_default_row(value=1, time_value=1), CovidcastTestRow.make_default_row(value=2, time_value=2),
    CovidcastTestRow.make_default_row(value=3, time_value=3)] with all the defaults from CovidcastTestRow.
    """
    # If any iterables were passed instead of lists, convert them to lists.
    kwargs = {key: list(value) for key, value in kwargs.items()}
    # All the arg values must be lists of the same length.
    assert len(set(len(lst) for lst in kwargs.values())) == 1

    if sanitize_fields:
        return [CovidcastTestRow.make_default_row(**_kwargs)._sanitize_fields(extra_checks=test_mode) for _kwargs in transpose_dict(kwargs)]
    else:
        return [CovidcastTestRow.make_default_row(**_kwargs) for _kwargs in transpose_dict(kwargs)]


def covidcast_rows_from_records(records: Iterable[dict], sanity_check: bool = False) -> List[CovidcastTestRow]:
    """A convenience constructor.

    Default is different from from_args, because from_records is usually called on faux-API returns in tests,
    where we don't want any values getting default filled in.

    You can use csv.DictReader before this to read a CSV file.
    """
    records = list(records)
    return [CovidcastTestRow.make_default_row(**record) if not sanity_check else
            CovidcastTestRow.make_default_row(**record)._sanitize_fields() for record in records]


def covidcast_rows_as_dicts(rows: Iterable[CovidcastTestRow], ignore_fields: Optional[List[str]] = None) -> List[dict]:
    return [row.as_dict(ignore_fields=ignore_fields) for row in rows]


def covidcast_rows_as_dataframe(rows: Iterable[CovidcastTestRow], ignore_fields: Optional[List[str]] = None) -> pd.DataFrame:
    if ignore_fields is None:
        ignore_fields = []

    columns = [field.name for field in fields(CovidcastTestRow) if field.name not in ignore_fields]

    if rows:
        df = pd.concat([row.as_dataframe(ignore_fields=ignore_fields) for row in rows], ignore_index=True)
        return df[columns]
    else:
        return pd.DataFrame(columns=columns)


def covidcast_rows_as_api_row_df(rows: Iterable[CovidcastTestRow]) -> pd.DataFrame:
    return covidcast_rows_as_dataframe(rows, ignore_fields=CovidcastTestRow._api_row_ignore_fields)


def covidcast_rows_as_api_compatibility_row_df(rows: Iterable[CovidcastTestRow]) -> pd.DataFrame:
    return covidcast_rows_as_dataframe(rows, ignore_fields=CovidcastTestRow._api_row_compatibility_ignore_fields)


def covidcast_rows_as_db_row_df(rows: Iterable[CovidcastTestRow]) -> pd.DataFrame:
    return covidcast_rows_as_dataframe(rows, ignore_fields=CovidcastTestRow._db_row_ignore_fields)


def transpose_dict(d: Dict[Any, List[Any]]) -> List[Dict[Any, Any]]:
    """Given a dictionary whose values are lists of the same length, turn it into a list of dictionaries whose values are the individual list entries.

    Example:
    >>> transpose_dict(dict([["a", [2, 4, 6]], ["b", [3, 5, 7]], ["c", [10, 20, 30]]]))
    [{"a": 2, "b": 3, "c": 10}, {"a": 4, "b": 5, "c": 20}, {"a": 6, "b": 7, "c": 30}]
    """
    return [dict(zip(d.keys(), values)) for values in zip(*d.values())]


def assert_frame_equal_no_order(df1: pd.DataFrame, df2: pd.DataFrame, index: List[str], **kwargs: Any) -> None:
    """Assert that two DataFrames are equal, ignoring the order of rows."""
    # Remove any existing index. If it wasn't named, drop it. Set a new index and sort it.
    df1 = df1.reset_index().drop(columns="index").set_index(index).sort_index()
    df2 = df2.reset_index().drop(columns="index").set_index(index).sort_index()
    pd.testing.assert_frame_equal(df1, df2, **kwargs)


class CovidcastBase(unittest.TestCase):
    def setUp(self):
        # use the local test instance of the database
        secrets.db.host = 'delphi_database_epidata'
        secrets.db.epi = ('user', 'pass')

        self._db = Database()
        self._db.connect()

        # empty all of the data tables
        for table in "epimetric_load  epimetric_latest  epimetric_full  geo_dim  signal_dim".split():
            self._db._cursor.execute(f"TRUNCATE TABLE {table};")
        self.localSetUp()
        self._db._connection.commit()

    def tearDown(self):
        # close and destroy conenction to the database
        self.localTearDown()
        self._db.disconnect(False)
        del self._db

    def localSetUp(self):
        # stub; override in subclasses to perform custom setup.
        # runs after tables have been truncated but before database changes have been committed
        pass

    def localTearDown(self):
        # stub; override in subclasses to perform custom teardown.
        # runs after database changes have been committed
        pass

    def _insert_rows(self, rows: Sequence[CovidcastTestRow]):
        # inserts rows into the database using the full acquisition process, including 'dbjobs' load into history & latest tables
        n = self._db.insert_or_update_bulk(rows)
        print(f"{n} rows added to load table & dispatched to v4 schema")
        # NOTE: this isnt expressly needed for our test cases, but would be if using external access (like through client lib)
        # To ensure changes are visible outside of this db session
        self._db._connection.commit()

    def params_from_row(self, row: CovidcastTestRow, **kwargs):
        ret = {
            'data_source': row.source,
            'signals': row.signal,
            'time_type': row.time_type,
            'geo_type': row.geo_type,
            'time_values': row.time_value,
            'geo_value': row.geo_value,
        }
        ret.update(kwargs)
        return ret
