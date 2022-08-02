from dataclasses import asdict, dataclass, field, fields
from datetime import date
from typing import Any, Dict, Iterable, List, Optional, Union, get_args, get_origin

from delphi_utils import Nans
from numpy import isnan
from pandas import DataFrame, concat

from .csv_importer import CsvRowValues
from ...server.utils.dates import date_to_time_value, time_value_to_date


def _is_none(v: Optional[float]) -> bool:
    return True if v is None or (v is not None and isnan(v)) else False

@dataclass
class CovidcastRow:
    """A container for (most of) the values of a single covidcast database row.

    Used for:
    - inserting rows into the database
    - quickly creating rows with default fields for testing

    The rows are specified in 'v4_schema.sql'.
    """

    source: str = "src"
    signal: str = "sig"
    time_type: str = "day"
    geo_type: str = "county"
    time_value: int = 20200202                  # Can be initialized with datetime.date
    geo_value: str = "01234"
    value: float = 10.0
    stderr: float = 10.0
    sample_size: float = 10.0
    missing_value: int = Nans.NOT_MISSING.value
    missing_stderr: int = Nans.NOT_MISSING.value
    missing_sample_size: int = Nans.NOT_MISSING.value
    issue: Optional[int] = 20200202                       # Can be initialized with datetime.date
    lag: Optional[int] = 0
    id: Optional[int] = None
    direction: Optional[int] = None
    direction_updated_timestamp: int = 0
    value_updated_timestamp: int = 20200202     # Can be initialized with datetime.date

    def __post_init__(self):
        # Convert time values to ints by default.
        self.time_value = date_to_time_value(self.time_value) if isinstance(self.time_value, date) else self.time_value
        self.issue = date_to_time_value(self.issue) if isinstance(self.issue, date) else self.issue
        self.value_updated_timestamp = date_to_time_value(self.value_updated_timestamp) if isinstance(self.value_updated_timestamp, date) else self.value_updated_timestamp

        # These specify common views into this object: 
        # - 1. If this row was returned by an API request
        self._api_row_ignore_fields = ["id", "direction", "direction_updated_timestamp", "value_updated_timestamp"]
        # - 2. If this row was returned by an old API request (PHP server)
        self._api_row_compatibility_ignore_fields = ["id", "direction", "direction_updated_timestamp", "value_updated_timestamp", "source"]
        # - 3. If this row was returned by the database.
        self._db_row_ignore_fields = []

    def _sanity_check_fields(self, test_mode: bool = True):
        if self.issue and self.issue < self.time_value:
            self.issue = self.time_value

        if self.issue:
            self.lag = (time_value_to_date(self.issue) - time_value_to_date(self.time_value)).days
        else:
            self.lag = None

        # This sanity checking is already done in CsvImporter, but it's here so the testing class gets it too.
        if _is_none(self.value) and self.missing_value == Nans.NOT_MISSING:
            self.missing_value = Nans.NOT_APPLICABLE.value if test_mode else Nans.OTHER.value

        if _is_none(self.stderr) and self.missing_stderr == Nans.NOT_MISSING:
            self.missing_stderr = Nans.NOT_APPLICABLE.value if test_mode else Nans.OTHER.value

        if _is_none(self.sample_size) and self.missing_sample_size == Nans.NOT_MISSING:
            self.missing_sample_size = Nans.NOT_APPLICABLE.value if test_mode else Nans.OTHER.value

        return self

    @staticmethod
    def fromCsvRowValue(row_value: Optional[CsvRowValues], source: str, signal: str, time_type: str, geo_type: str, time_value: int, issue: int, lag: int):
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
    def fromCsvRows(row_values: Iterable[Optional[CsvRowValues]], source: str, signal: str, time_type: str, geo_type: str, time_value: int, issue: int, lag: int):
        # NOTE: returns a generator, as row_values is expected to be a generator
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

    def as_dataframe(self, ignore_fields: Optional[List[str]] = None) -> DataFrame:
        return DataFrame.from_records([self.as_dict(ignore_fields=ignore_fields)])

    @property
    def api_row_df(self) -> DataFrame:
        """Returns a dataframe view into the row with the fields returned by the API server."""
        return self.as_dataframe(ignore_fields=self._api_row_ignore_fields)

    @property
    def api_compatibility_row_df(self) -> DataFrame:
        """Returns a dataframe view into the row with the fields returned by the old API server (the PHP server)."""
        return self.as_dataframe(ignore_fields=self._api_row_compatibility_ignore_fields)

    @property
    def db_row_df(self) -> DataFrame:
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
    rows: List[CovidcastRow] = field(default_factory=list)

    def __post_init__(self):
        # These specify common views into this object: 
        # - 1. If this row was returned by an API request
        self._api_row_ignore_fields = CovidcastRow()._api_row_ignore_fields
        # - 2. If this row was returned by an old API request (PHP server)
        self._api_row_compatibility_ignore_fields = CovidcastRow()._api_row_compatibility_ignore_fields
        # - 3. If this row was returned by the database.
        self._db_row_ignore_fields = CovidcastRow()._db_row_ignore_fields

        # Used to create a consistent DataFrame for tests.
        dtypes = {field.name: field.type if get_origin(field.type) is not Union else get_args(field.type)[0] for field in fields(CovidcastRow)}
        # Sometimes the int fields have None values, so we expand their scope using pandas.Int64DType.
        self._DTYPES = {key: value if value is not int else "Int64" for key, value in dtypes.items()}

    @staticmethod
    def from_args(sanity_check: bool = True, test_mode: bool = True, **kwargs: Dict[str, Iterable]):
        """A convenience constructor.

        Handy for constructing batches of test cases.

        Example:
        CovidcastRows.from_args(value=[1, 2, 3], time_value=[1, 2, 3]) will yield
        CovidcastRows(rows=[CovidcastRow(value=1, time_value=1), CovidcastRow(value=2, time_value=2), CovidcastRow(value=3, time_value=3)])
        with all the defaults from CovidcastRow.
        """
        # All the args must be fields of CovidcastRow.
        assert set(kwargs.keys()) <= set(field.name for field in fields(CovidcastRow))

        # If any iterables were passed instead of lists, convert them to lists.
        kwargs = {key: list(value) for key, value in kwargs.items()}

        # All the arg values must be lists of the same length.
        assert len(set(len(lst) for lst in kwargs.values())) == 1

        return CovidcastRows(rows=[CovidcastRow(**_kwargs)._sanity_check_fields(test_mode=test_mode) if sanity_check else CovidcastRow(**_kwargs) for _kwargs in transpose_dict(kwargs)])

    @staticmethod
    def from_records(records: Iterable[dict], sanity_check: bool = False):
        """A convenience constructor.
        
        Default is different from from_args, because from_records is usually called on faux-API returns in tests,
        where we don't want any values getting default filled in.
        """
        records = list(records)
        assert set().union(*[record.keys() for record in records]) <= set(field.name for field in fields(CovidcastRow))

        return CovidcastRows(rows=[CovidcastRow(**record) if not sanity_check else CovidcastRow(**record)._sanity_check_fields() for record in records])

    def as_dicts(self, ignore_fields: Optional[List[str]] = None) -> List[dict]:
        return [row.as_dict(ignore_fields=ignore_fields) for row in self.rows]

    def as_dataframe(self, ignore_fields: Optional[List[str]] = None) -> DataFrame:
        if ignore_fields is None:
            ignore_fields = []
        columns = [field.name for field in fields(CovidcastRow) if field.name not in ignore_fields]
        if self.rows:
            df = concat([row.as_dataframe(ignore_fields=ignore_fields) for row in self.rows], ignore_index=True)
            df = set_df_dtypes(df, self._DTYPES)
            return df[columns]
        else:
            return DataFrame(columns=columns)

    @property
    def api_row_df(self) -> DataFrame:
        return self.as_dataframe(ignore_fields=self._api_row_ignore_fields)

    @property
    def api_compatibility_row_df(self) -> DataFrame:
        return self.as_dataframe(ignore_fields=self._api_row_compatibility_ignore_fields)

    @property
    def db_row_df(self) -> DataFrame:
        return self.as_dataframe(ignore_fields=self._db_row_ignore_fields)


def transpose_dict(d: Dict[Any, List[Any]]) -> List[Dict[Any, Any]]:
    """Given a dictionary whose values are lists of the same length, turn it into a list of dictionaries whose values are the individual list entries.

    Example:
    >>> transpose_dict(dict([["a", [2, 4, 6]], ["b", [3, 5, 7]], ["c", [10, 20, 30]]]))
    [{"a": 2, "b": 3, "c": 10}, {"a": 4, "b": 5, "c": 20}, {"a": 6, "b": 7, "c": 30}]
    """
    return [dict(zip(d.keys(), values)) for values in zip(*d.values())]


def set_df_dtypes(df: DataFrame, dtypes: Dict[str, Any]) -> DataFrame:
    """Set the dataframe column datatypes.
    df: pd.DataFrame
        The dataframe to change.
    dtypes: Dict[str, Any]
        The keys of the dict are columns and the values are either types or Pandas
        string aliases for types. Not all columns are required.
    """
    assert all(isinstance(e, type) or isinstance(e, str) for e in dtypes.values()), "Values must be types or Pandas string aliases for types."

    df = df.copy()
    for k, v in dtypes.items():
        if k in df.columns:
            df[k] = df[k].astype(v)
    return df
