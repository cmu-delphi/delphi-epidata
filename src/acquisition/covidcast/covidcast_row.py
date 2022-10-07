from dataclasses import asdict, dataclass, field, fields
from datetime import date
from typing import Any, ClassVar, Dict, Iterable, List, Optional

import pandas as pd
from delphi_utils import Nans

from delphi.epidata.acquisition.covidcast.csv_importer import CsvImporter
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
    source: str = "src"
    signal: str = "sig"
    time_type: str = "day"
    geo_type: str = "county"
    time_value: int = 20200202
    geo_value: str = "01234"
    value: float = 10.0
    stderr: float = 10.0
    sample_size: float = 10.0
    missing_value: int = Nans.NOT_MISSING.value
    missing_stderr: int = Nans.NOT_MISSING.value
    missing_sample_size: int = Nans.NOT_MISSING.value
    issue: Optional[int] = 20200202
    lag: Optional[int] = 0
    id: Optional[int] = None
    direction: Optional[int] = None
    direction_updated_timestamp: int = 0
    value_updated_timestamp: int = 20200202

    # Classvars.
    _api_row_ignore_fields: ClassVar = ["id", "direction_updated_timestamp", "value_updated_timestamp"]
    _api_row_compatibility_ignore_fields: ClassVar = ["id", "direction_updated_timestamp", "value_updated_timestamp", "source"]
    _db_row_ignore_fields: ClassVar = []
    _pandas_dtypes: ClassVar = PANDAS_DTYPES

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

    @staticmethod
    def fromCsvRowValue(row_value: Optional[CsvImporter.RowValues], source: str, signal: str, time_type: str, geo_type: str, time_value: int, issue: int, lag: int):
        """Create a CovidcastRow from a CsvImporter.RowValues object.
        
        Used in covidcast acquisition. 
        """
        if row_value is None:
            return None
        return CovidcastRow(
            source,
            signal,
            time_type,
            geo_type,
            time_value,
            row_value.geo_value,
            row_value.value,
            row_value.stderr,
            row_value.sample_size,
            row_value.missing_value,
            row_value.missing_stderr,
            row_value.missing_sample_size,
            issue,
            lag,
        )

    @staticmethod
    def fromCsvRows(row_values: Iterable[Optional[CsvImporter.RowValues]], source: str, signal: str, time_type: str, geo_type: str, time_value: int, issue: int, lag: int):
        """Create a generator of CovidcastRow from a list of CsvImporter.RowValues objects.
        
        Used in covidcast acquisition.
        """
        return (CovidcastRow.fromCsvRowValue(row_value, source, signal, time_type, geo_type, time_value, issue, lag) for row_value in row_values)

    @staticmethod
    def from_json(json: Dict[str, Any]) -> "CovidcastRow":
        return CovidcastRow(
            source=json["source"],
            signal=json["signal"],
            time_type=json["time_type"],
            geo_type=json["geo_type"],
            geo_value=json["geo_value"],
            issue=json["issue"],
            lag=json["lag"],
            value=json["value"],
            stderr=json["stderr"],
            sample_size=json["sample_size"],
            missing_value=json["missing_value"],
            missing_stderr=json["missing_stderr"],
            missing_sample_size=json["missing_sample_size"],
        )

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


@dataclass
class CovidcastRows:
    # Arguments.
    rows: List[CovidcastRow] = field(default_factory=list)

    # Classvars.
    _api_row_ignore_fields: ClassVar = CovidcastRow._api_row_ignore_fields
    _api_row_compatibility_ignore_fields: ClassVar = CovidcastRow._api_row_compatibility_ignore_fields
    _db_row_ignore_fields: ClassVar = CovidcastRow._db_row_ignore_fields
    _pandas_dtypes: ClassVar = CovidcastRow._pandas_dtypes

    @staticmethod
    def from_args(sanity_check: bool = True, test_mode: bool = True, **kwargs: Dict[str, Iterable]):
        """A convenience constructor.

        Handy for constructing batches of test cases.

        Example:
        CovidcastRows.from_args(value=[1, 2, 3], time_value=[1, 2, 3]) will yield
        CovidcastRows(rows=[CovidcastRow(value=1, time_value=1), CovidcastRow(value=2, time_value=2), CovidcastRow(value=3, time_value=3)])
        with all the defaults from CovidcastRow.
        """
        # If any iterables were passed instead of lists, convert them to lists.
        kwargs = {key: list(value) for key, value in kwargs.items()}
        # All the arg values must be lists of the same length.
        assert len(set(len(lst) for lst in kwargs.values())) == 1
        return CovidcastRows(rows=[CovidcastRow(**_kwargs) if not sanity_check else CovidcastRow(**_kwargs)._sanity_check_fields(extra_checks=test_mode) for _kwargs in transpose_dict(kwargs)])

    @staticmethod
    def from_records(records: Iterable[dict], sanity_check: bool = False):
        """A convenience constructor.

        Default is different from from_args, because from_records is usually called on faux-API returns in tests,
        where we don't want any values getting default filled in.

        You can use csv.DictReader before this to read a CSV file.
        """
        records = list(records)
        return CovidcastRows(rows=[CovidcastRow(**record) if not sanity_check else CovidcastRow(**record)._sanity_check_fields() for record in records])

    def as_dicts(self, ignore_fields: Optional[List[str]] = None) -> List[dict]:
        return [row.as_dict(ignore_fields=ignore_fields) for row in self.rows]

    def as_dataframe(self, ignore_fields: Optional[List[str]] = None) -> pd.DataFrame:
        if ignore_fields is None:
            ignore_fields = []
        columns = [field.name for field in fields(CovidcastRow) if field.name not in ignore_fields]
        if self.rows:
            df = pd.concat([row.as_dataframe(ignore_fields=ignore_fields) for row in self.rows], ignore_index=True)
            return df[columns]
        else:
            return pd.DataFrame(columns=columns)

    @property
    def api_row_df(self) -> pd.DataFrame:
        return self.as_dataframe(ignore_fields=self._api_row_ignore_fields)

    @property
    def api_compatibility_row_df(self) -> pd.DataFrame:
        return self.as_dataframe(ignore_fields=self._api_row_compatibility_ignore_fields)

    @property
    def db_row_df(self) -> pd.DataFrame:
        return self.as_dataframe(ignore_fields=self._db_row_ignore_fields)


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
