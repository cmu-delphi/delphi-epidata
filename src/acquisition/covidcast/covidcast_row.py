from dataclasses import asdict, dataclass
from typing import Any, ClassVar, Dict, List, Optional

import pandas as pd


PANDAS_DTYPES = {
    "source": str,
    "signal": str,
    "time_type": str,
    "time_value": "Int64",
    "geo_type": str,
    "geo_value": str,
    "value": float,
    "stderr": float,
    "sample_size": float,
    "missing_value": "Int8",
    "missing_stderr": "Int8",
    "missing_sample_size": "Int8",
    "issue": "Int64",
    "lag": "Int64",
    "id": "Int64",
    "direction": "Int8",
    "direction_updated_timestamp": "Int64",
    "value_updated_timestamp": "Int64",
}

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
    issue: int
    lag: int
    # The following three fields are only the database, but are not ingested at acquisition and not returned by the API.
    epimetric_id: Optional[int] = None
    direction: Optional[int] = None
    value_updated_timestamp: Optional[int] = 0

    # Classvars.
    _db_row_ignore_fields: ClassVar = []
    _api_row_ignore_fields: ClassVar = ["epimetric_id", "value_updated_timestamp"]
    _api_row_compatibility_ignore_fields: ClassVar = _api_row_ignore_fields + ["source", "time_type", "geo_type"]

    _pandas_dtypes: ClassVar = PANDAS_DTYPES

    def as_dict(self, ignore_fields: Optional[List[str]] = None) -> dict:
        d = asdict(self)
        if ignore_fields:
            for key in ignore_fields:
                del d[key]
        return d
    
    def as_api_row_dict(self, ignore_fields: Optional[List[str]] = None) -> dict:
        """Returns a dict view into the row with the fields returned by the API server."""
        return self.as_dict(ignore_fields=self._api_row_ignore_fields + (ignore_fields or []))

    def as_api_compatibility_row_dict(self, ignore_fields: Optional[List[str]] = None) -> dict:
        """Returns a dict view into the row with the fields returned by the old API server (the PHP server)."""
        return self.as_dict(ignore_fields=self._api_row_compatibility_ignore_fields + (ignore_fields or []))

    def as_db_row_dict(self, ignore_fields: Optional[List[str]] = None) -> dict:
        """Returns a dict view into the row with the fields returned by the database."""
        return self.as_dict(ignore_fields=self._db_row_ignore_fields + (ignore_fields or []))

    def as_dataframe(self, ignore_fields: Optional[List[str]] = None) -> pd.DataFrame:
        df = pd.DataFrame.from_records([self.as_dict(ignore_fields=ignore_fields)])
        # This is to mirror the types in model.py.
        df = set_df_dtypes(df, self._pandas_dtypes)
        return df

    def as_api_row_df(self, ignore_fields: Optional[List[str]] = None) -> pd.DataFrame:
        """Returns a dataframe view into the row with the fields returned by the API server."""
        return self.as_dataframe(ignore_fields=self._api_row_ignore_fields + (ignore_fields or []))

    def as_api_compatibility_row_df(self, ignore_fields: Optional[List[str]] = None) -> pd.DataFrame:
        """Returns a dataframe view into the row with the fields returned by the old API server (the PHP server)."""
        return self.as_dataframe(ignore_fields=self._api_row_compatibility_ignore_fields + (ignore_fields or []))

    def as_db_row_df(self, ignore_fields: Optional[List[str]] = None) -> pd.DataFrame:
        """Returns a dataframe view into the row with the fields returned by an all-field database query."""
        return self.as_dataframe(ignore_fields=self._db_row_ignore_fields + (ignore_fields or []))

    def signal_pair(self):
        return f"{self.source}:{self.signal}"

    def geo_pair(self):
        return f"{self.geo_type}:{self.geo_value}"

    def time_pair(self):
        return f"{self.time_type}:{self.time_value}"



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
