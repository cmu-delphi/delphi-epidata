"""
Convenience dataclasses for testing.
"""
from dataclasses import dataclass, asdict
from datetime import date
from typing import Any, Callable, Dict, List, Optional, Union

from pandas import DataFrame

from .dates import date_to_time_value
from delphi_utils.nancodes import Nans


def apply_kwargs(func: Callable, **kwargs: Dict[Any, List]) -> List:
    """
    Applies func, a function with all keyword args, to each tuple in kwargs. It is
    best to see an example.

    Example 1:
    >>>apply_kwargs(f, a=[3, 2, 1], b=[1, 1, 5])
    [f(a=3, b=1), f(a=2, b=1), f(a=1, b=5)]
    >>>apply_kwargs(f, a=[3, 2, 1])
    [f(a=3), f(a=2), f(a=1)]

    Example 2:
    >>>def f(a=5, b=5):
    >>>    return (a, b)
    >>>apply_kwargs(f, a=[3, 2])
    [(3, 5), (2, 5)]
    >>>apply_kwargs(f, a=[3, 2, 1], b=[1, 1, 5])
    [(3, 1), (2, 1)]
    """
    # Length of first key's array.
    firstkey, firstvalue = iter(kwargs.items()).__next__()
    n = len(firstvalue)

    # Check length of all inputs match.
    if not all(len(value) == n for value in kwargs.values() if isinstance(value, list)):
        keys = [firstkey] + [key for key, value in kwargs.items() if isinstance(value, list) and len(value) != n]
        raise ValueError(f"Length of all arrays does not match. Keys that don't match: {keys}.")

    # For each index in the lists, make a set of function args (like a zip, but with keyword names).
    out = []
    for i in range(n):
        fargs = dict()
        for key in kwargs:
            fargs.setdefault(key, kwargs[key][i])
        out.append(func(**fargs))
    return out


@dataclass
class CovidcastRecordCompatibility:
    signal: str = "sig"
    geo_type: str = "state"
    geo_value: str = "ca"
    time_value: Union[int, date] = date(2021, 5, 1)
    value: Optional[float] = 1.0
    stderr: Optional[float] = 1.0
    sample_size: Optional[float] = 1.0
    missing_value: Optional[int] = Nans.NOT_MISSING
    missing_stderr: Optional[int] = Nans.NOT_MISSING
    missing_sample_size: Optional[int] = Nans.NOT_MISSING

    def __post_init__(self):
        if isinstance(self.time_value, date):
            self.time_value = date_to_time_value(self.time_value)
        if self.value is None and self.missing_value == Nans.NOT_MISSING:
            self.missing_value = Nans.NOT_APPLICABLE
        if self.stderr is None and self.missing_stderr == Nans.NOT_MISSING:
            self.missing_stderr = Nans.NOT_APPLICABLE
        if self.sample_size is None and self.missing_sample_size == Nans.NOT_MISSING:
            self.missing_sample_size = Nans.NOT_APPLICABLE


@dataclass
class CovidcastRecord(CovidcastRecordCompatibility):
    source: str = "src"


@dataclass
class CovidcastRecords:
    sources: Optional[List[str]] = None
    signals: Optional[List[str]] = None
    geo_types: Optional[List[str]] = None
    geo_values: Optional[List[str]] = None
    time_values: Optional[List[Union[date, int]]] = None
    values: Optional[List[float]] = None
    stderrs: Optional[List[float]] = None
    sample_sizes: Optional[List[float]] = None
    missing_values: Optional[List[int]] = None
    missing_stderrs: Optional[List[int]] = None
    missing_sample_sizes: Optional[List[int]] = None
    is_compatibility: bool = False

    def as_records(self):
        kwargs = {}
        if self.sources is not None and not self.is_compatibility:
            kwargs["source"] = list(self.sources)
        if self.signals is not None:
            kwargs["signal"] = list(self.signals)
        if self.geo_types is not None:
            kwargs["geo_types"] = list(self.geo_types)
        if self.geo_values is not None:
            kwargs["geo_value"] = list(self.geo_values)
        if self.time_values is not None:
            kwargs["time_value"] = list(self.time_values)
        if self.values is not None:
            kwargs["value"] = list(self.values)
        if self.stderrs is not None:
            kwargs["stderr"] = list(self.stderrs)
        if self.sample_sizes is not None:
            kwargs["sample_size"] = list(self.sample_sizes)
        if self.missing_values is not None:
            kwargs["missing_value"] = list(self.missing_values)
        if self.missing_stderrs is not None:
            kwargs["missing_stderr"] = list(self.missing_stderrs)
        if self.missing_sample_sizes is not None:
            kwargs["missing_sample_size"] = list(self.missing_sample_sizes)

        return apply_kwargs(CovidcastRecordCompatibility if self.is_compatibility else CovidcastRecord, **kwargs)

    def as_dicts(self):
        return [asdict(record) for record in self.as_records()]

    def as_dataframe(self):
        columns = ([] if self.is_compatibility else ["source"]) + [
            "signal", "geo_type", "geo_value", "time_value", "value", "stderr", "sample_size", "missing_value", "missing_stderr", "missing_sample_size"
        ]
        return DataFrame.from_records(self.as_dicts(), columns=columns)
