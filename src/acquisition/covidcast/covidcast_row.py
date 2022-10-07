from dataclasses import asdict, dataclass, fields
from datetime import date
from typing import Any, ClassVar, Dict, Iterable, List, Optional

import pandas as pd
from delphi_utils import Nans

from delphi.epidata.server.utils.dates import day_to_time_value, time_value_to_day
from delphi.epidata.server.endpoints.covidcast_utils.model import PANDAS_DTYPES


@dataclass
class CovidcastRow:
    """A container for the values of a single covidcast database row.

    Used for:
    - inserting rows into the database
    - creating test rows with default fields for testing
    - converting from and to formats (dict, csv, df, kwargs)
    - creating consistent views, with consistent data types (dict, csv, df)

    The rows are specified in 'v4_schema.sql'. The datatypes are made to match database. When writing to Pandas, the dtypes match the JIT model.py schema.
    """

    # Arguments.
    source: str
    signal: str
    time_type: str
    geo_type: str
    time_value: int
    geo_value: str
    value: float
    stderr: float
    sample_size: float
    # The following three fields are Nans enums from delphi_utils.nans.
    missing_value: int
    missing_stderr: int
    missing_sample_size: int
    issue: Optional[int]
    lag: Optional[int]
    # The following four fields are only the database, but are not ingested at acquisition and not returned by the API.
    id: Optional[int]
    direction: Optional[int]
    direction_updated_timestamp: int
    value_updated_timestamp: int

    # Classvars.
    _db_row_ignore_fields: ClassVar = []
    _api_row_ignore_fields: ClassVar = ["id", "direction_updated_timestamp", "value_updated_timestamp"]
    _api_row_compatibility_ignore_fields: ClassVar = ["id", "direction_updated_timestamp", "value_updated_timestamp", "source", "time_type", "geo_type"]
    _pandas_dtypes: ClassVar = PANDAS_DTYPES

    @staticmethod
    def make_default_row(**kwargs) -> "CovidcastRow":
        default_args = {
            "source": "src",
            "signal": "sig",
            "time_type": "day",
            "geo_type": "county",
            "time_value": 20200202,
            "geo_value": "01234",
            "value": 10.0,
            "stderr": 10.0,
            "sample_size": 10.0,
            "missing_value": Nans.NOT_MISSING.value,
            "missing_stderr": Nans.NOT_MISSING.value,
            "missing_sample_size": Nans.NOT_MISSING.value,
            "issue": 20200202,
            "lag": 0,
            "id": None,
            "direction": None,
            "direction_updated_timestamp": 0,
            "value_updated_timestamp": 20200202,
        }
        default_args.update(kwargs)
        return CovidcastRow(**default_args)

    def __post_init__(self):
        # Convert time values to ints by default.
        self.time_value = day_to_time_value(self.time_value) if isinstance(self.time_value, date) else self.time_value
        self.issue = day_to_time_value(self.issue) if isinstance(self.issue, date) else self.issue
        self.value_updated_timestamp = day_to_time_value(self.value_updated_timestamp) if isinstance(self.value_updated_timestamp, date) else self.value_updated_timestamp

    def _sanity_check_fields(self, extra_checks: bool = True):
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

    def as_dict(self, ignore_fields: Optional[List[str]] = None) -> dict:
        d = asdict(self)
        if ignore_fields:
            for key in ignore_fields:
                del d[key]
        return d

    def as_dataframe(self, ignore_fields: Optional[List[str]] = None) -> pd.DataFrame:
        df = pd.DataFrame.from_records([self.as_dict(ignore_fields=ignore_fields)])
        # This is to mirror the types in model.py.
        df = set_df_dtypes(df, self._pandas_dtypes)
        return df

    @property
    def api_row_df(self) -> pd.DataFrame:
        """Returns a dataframe view into the row with the fields returned by the API server."""
        return self.as_dataframe(ignore_fields=self._api_row_ignore_fields)

    @property
    def api_compatibility_row_df(self) -> pd.DataFrame:
        """Returns a dataframe view into the row with the fields returned by the old API server (the PHP server)."""
        return self.as_dataframe(ignore_fields=self._api_row_compatibility_ignore_fields)

    @property
    def db_row_df(self) -> pd.DataFrame:
        """Returns a dataframe view into the row with the fields returned by an all-field database query."""
        return self.as_dataframe(ignore_fields=self._db_row_ignore_fields)

    @property
    def signal_pair(self):
        return f"{self.source}:{self.signal}"

    @property
    def geo_pair(self):
        return f"{self.geo_type}:{self.geo_value}"

    @property
    def time_pair(self):
        return f"{self.time_type}:{self.time_value}"


def covidcast_rows_from_args(sanity_check: bool = True, test_mode: bool = True, **kwargs: Dict[str, Iterable]) -> List[CovidcastRow]:
    """A convenience constructor.

    Handy for constructing batches of test cases.

    Example:
    covidcast_rows_from_args(value=[1, 2, 3], time_value=[1, 2, 3]) will yield
    [CovidcastRow.make_default_row(value=1, time_value=1), CovidcastRow.make_default_row(value=2, time_value=2), CovidcastRow.make_default_row(value=3, time_value=3)]
    with all the defaults from CovidcastRow.
    """
    # If any iterables were passed instead of lists, convert them to lists.
    kwargs = {key: list(value) for key, value in kwargs.items()}
    # All the arg values must be lists of the same length.
    assert len(set(len(lst) for lst in kwargs.values())) == 1

    if sanity_check:
        return [CovidcastRow.make_default_row(**_kwargs)._sanity_check_fields(extra_checks=test_mode) for _kwargs in transpose_dict(kwargs)]
    else:
        return [CovidcastRow.make_default_row(**_kwargs) for _kwargs in transpose_dict(kwargs)]


def covidcast_rows_from_records(records: Iterable[dict], sanity_check: bool = False) -> List[CovidcastRow]:
    """A convenience constructor.

    Default is different from from_args, because from_records is usually called on faux-API returns in tests,
    where we don't want any values getting default filled in.

    You can use csv.DictReader before this to read a CSV file.
    """
    records = list(records)
    return [CovidcastRow.make_default_row(**record) if not sanity_check else CovidcastRow.make_default_row(**record)._sanity_check_fields() for record in records]


def covidcast_rows_as_dicts(rows: Iterable[CovidcastRow], ignore_fields: Optional[List[str]] = None) -> List[dict]:
    return [row.as_dict(ignore_fields=ignore_fields) for row in rows]


def covidcast_rows_as_dataframe(rows: Iterable[CovidcastRow], ignore_fields: Optional[List[str]] = None) -> pd.DataFrame:
    if ignore_fields is None:
        ignore_fields = []

    columns = [field.name for field in fields(CovidcastRow) if field.name not in ignore_fields]

    if rows:
        df = pd.concat([row.as_dataframe(ignore_fields=ignore_fields) for row in rows], ignore_index=True)
        return df[columns]
    else:
        return pd.DataFrame(columns=columns)


def covidcast_rows_as_api_row_df(rows: Iterable[CovidcastRow]) -> pd.DataFrame:
    return covidcast_rows_as_dataframe(rows, ignore_fields=CovidcastRow._api_row_ignore_fields)


def covidcast_rows_as_api_compatibility_row_df(rows: Iterable[CovidcastRow]) -> pd.DataFrame:
    return covidcast_rows_as_dataframe(rows, ignore_fields=CovidcastRow._api_row_compatibility_ignore_fields)


def covidcast_rows_as_db_row_df(rows: Iterable[CovidcastRow]) -> pd.DataFrame:
    return covidcast_rows_as_dataframe(rows, ignore_fields=CovidcastRow._db_row_ignore_fields)


def transpose_dict(d: Dict[Any, List[Any]]) -> List[Dict[Any, Any]]:
    """Given a dictionary whose values are lists of the same length, turn it into a list of dictionaries whose values are the individual list entries.

    Example:
    >>> transpose_dict(dict([["a", [2, 4, 6]], ["b", [3, 5, 7]], ["c", [10, 20, 30]]]))
    [{"a": 2, "b": 3, "c": 10}, {"a": 4, "b": 5, "c": 20}, {"a": 6, "b": 7, "c": 30}]
    """
    return [dict(zip(d.keys(), values)) for values in zip(*d.values())]


def check_valid_dtype(dtype):
    try:
        pd.api.types.pandas_dtype(dtype)
    except TypeError:
        raise ValueError(f"Invalid dtype {dtype}")


def set_df_dtypes(df: pd.DataFrame, dtypes: Dict[str, Any]) -> pd.DataFrame:
    """Set the dataframe column datatypes."""
    [check_valid_dtype(d) for d in dtypes.values()]

    df = df.copy()
    for k, v in dtypes.items():
        if k in df.columns:
            df[k] = df[k].astype(v)
    return df


def assert_frame_equal_no_order(df1: pd.DataFrame, df2: pd.DataFrame, index: List[str], **kwargs: Any) -> None:
    """Assert that two DataFrames are equal, ignoring the order of rows."""
    # Remove any existing index. If it wasn't named, drop it. Set a new index and sort it.
    df1 = df1.reset_index().drop(columns="index").set_index(index).sort_index()
    df2 = df2.reset_index().drop(columns="index").set_index(index).sort_index()
    pd.testing.assert_frame_equal(df1, df2, **kwargs)
