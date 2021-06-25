from collections import ChainMap
from dataclasses import dataclass, asdict
from itertools import groupby, chain
from typing import Iterable, Dict, Callable, List, Optional, Union, Tuple

from more_itertools import windowed, dotproduct, peekable
from pandas import date_range, Timedelta
from numpy import NaN, isnan

from ..._params import SourceSignalPair


@dataclass
class SmoothResult:
    geo_type: str
    geo_value: str
    signal_source: str
    signal_signal: str

def _smoother(values: List[float], kernel: List[float] = None) -> float:
    """Basic smoother.

    By default, computes the standard mean. If kernel passed, uses the kernel
    as summation weights.
    """
    kernel = [1/len(values)] * len(values) if kernel is None else kernel
    if len(kernel) > len(values):
        kernel = kernel[-len(values):]
    elif len(kernel) < len(values):
        raise ValueError("Length of kernel is smaller than the length of values.")

    smoothed_value = dotproduct(values, kernel)
    return smoothed_value

def _pad_group(group: Iterable[Dict], pad_length: int, pad_fill_value: Union[float, str] = NaN) -> Iterable[Dict]:
    """Prepend window with pad_length many values."""

    # Peek the first element for the date, fill value, and other data entries.
    group = peekable(group)
    start_entry = group.peek().copy()

    # Get the time bounds.
    right_bound = start_entry["timestamp"] - Timedelta(1, unit="D")
    left_bound = start_entry["timestamp"] - Timedelta(pad_length, unit="D")

    if isinstance(pad_fill_value, str) and pad_fill_value == "first":
        padded_values = (dict(ChainMap({"timestamp": date}, start_entry)) for date in date_range(left_bound, right_bound))
    elif isinstance(pad_fill_value, str) and pad_fill_value == "drop":
        padded_values = (dict(ChainMap({"timestamp": date, "value": "drop"}, start_entry)) for date in date_range(left_bound, right_bound))
    elif isinstance(pad_fill_value, str):
        raise ValueError("String value of pad_fill_value can only be 'first' or 'drop'.")
    elif isinstance(pad_fill_value, (float, int)):
        padded_values = (dict(ChainMap({"timestamp": date, "value": pad_fill_value}, start_entry)) for date in date_range(left_bound, right_bound))
    else:
        raise ValueError("pad_fill_value should be a float or 'first' or 'drop'.")
    return chain(padded_values, group)

def _is_none_type(value: Optional[float]) -> bool:
    if isinstance(value, float) and isnan(value):
        return True
    elif value is None:
        return True
    return False

def generate_smooth_rows(
    # source: str,
    # signal: str,
    rows: Iterable[Dict],
    smooth_values: Callable[[List[float]], float] = _smoother,
    window_length: int = 7,
    pad_length: int = 6,
    pad_fill_value: Optional[float] = None,
    nan_fill_value: float = NaN) -> Iterable[Dict]:
    """Generate smoothed row entries.

    There are roughly two modes of boundary handling:
    * no padding, the windows start at length 1 on the left boundary and grow to size
      window_length (achieved with pad_fill_value = None)
    * value padding, window_length - 1 many fill_values are appended at the start of the
      given date (achieved with any other pad_fill_value)

    Note that this function crucially relies on the assumption that the iterable rows
    has been pre-sorted by geo_value and by timestamp. If this assumption is violated,
    the results will likely be incoherent.

    Parameters
    ----------
    rows: Iterable[Dict]
        An iterable over the rows a database query returns. The rows are assumed to be
        dicts containing the "geo_type", "geo_value", and "timestamp" keys. Assumes the
        rows have been sorted by geo and timestamp beforehand.
    smooth_values: Callable[[List[float]], float], default smoother
        A function taking a list of floats and producing a smoothed value. The smoothed
        value is placed in the timestamp of the last entry in the list of floats.
    window_length: int, default 7
        The smoothing window for length for the smoother.
    pad_length: int, default 6
        Number of fill_value values to prepend to each group. Set to window_length-1
        to get a value for each timestamp in rows. This helps generates a slide into an iterable's
        items. Assumed to be less than window_length.
    pad_fill_value: float, None, "first", default None
        The value to use when padding. If None, then the initial windows are made dynamic like
        (group[0]), (group[0], group[1]), ..., (group[0], group[1], ..., group[smoothed_window_length]).
        If "first", then the value from the first entry is used for filling.
    nan_fill_value: float, default NaN
        The value to use when encountering nans. By default, conforms None and numpy.nan types to numpy.nan.
        This will propagate nans. Otherwise, uses a float value.
    """
    assert pad_length < window_length

    for key, group in groupby(rows, lambda row: (row["geo_type"], row["geo_value"])): # Iterable[Tuple[str, Iterable[Dict]]]
        group = _pad_group(group, pad_length, pad_fill_value) if pad_fill_value is not None else _pad_group(group, pad_length, "drop")
        for window in windowed(group, window_length): # Iterable[List[Dict]]
            smoothed_entry = window[-1].copy() # last timestamp of window
            if pad_fill_value is not None:
                values = [entry["value"] if not _is_none_type(entry["value"]) else nan_fill_value for entry in window]
            else:
                values = [entry["value"] if not _is_none_type(entry["value"]) else nan_fill_value for entry in window if entry["value"] != "drop"]
            smoothed_entry["value"] = smooth_values(values)
            # smoothed_entry["source"] = source
            # smoothed_entry["signal"] = signal
            breakpoint()
            yield smoothed_entry

def generate_row_diffs(rows: Iterable[Dict], pad_fill_value: Optional[Union[str, float]] = None) -> Iterable[Dict]:
    """Generate differences between row values.

    Note that this function crucially relies on the assumption that the iterable rows
    has been pre-sorted by geo_value and by timestamp. If this assumption is violated,
    the results will likely be incoherent.

    rows: Iterable[Dict]
        An iterable over the rows a database query returns. The rows are assumed to be
        dicts containing the "geo_type", "geo_value", and "timestamp" keys. Assumes the
        rows have been sorted by geo and timestamp beforehand.
    pad_fill_value: Optional[Union[str, float]] or "first", default None
        The value used to prepend rows. If "first", then uses the first value of rows.
        If None, then no padding is used and the resulting iterable is shorter than the
        original by 1.
    """
    for _, group in groupby(rows, lambda row: (row["geo_type"], row["geo_value"])): # Iterable[Tuple[str, Iterable[Dict]]]
        group = _pad_group(group, 1, pad_fill_value) if pad_fill_value is not None else group
        for window in windowed(group, 2):
            incidence_entry = window[-1].copy()
            incidence_entry["value"] = window[1]["value"] - window[0]["value"]
            yield incidence_entry

def generate_prop_signal(rows: Iterable[Dict], pad_fill_value: Optional[Union[str, float]] = None) -> Iterable[Dict]:
    """Generate prop signal.

    May be more effort than its worth, given that the included geos are source-dependent.
    For example, when calculating the prop values in the JHU indicator, we use the formula
        incidence = (new counts) / population(geo) * 10**5
    The population(geo) quantity is calculated via an elaborate logic:
        * if geo is a county and is in {"78000", "69000", "66000", "60000"} (US territories), then
        population(geo) is given by previously-known values for these states
        * if geo is a county and is not a US territory, then the county population is used
        * if geo is state, hhs, or nation, then we total the member counties to find population(geo);
        "unassigned" category values are added in (no population(geo) contribution) to the numerator
        * if geo is hrr or msa, then we total the member counties to find population(geo);
        "unassigned" category values are not added to the numerator

    Let's leave aside the complexity of this logic combining with logic from other indicators like USAFacts
    and Safegraph. It is clear that calculating state, hhs, or nation denominators requires knowing the
    reporting counties on each day, which would go against a streaming architecture.
    """
    pass
