from collections import ChainMap
from itertools import groupby, chain
from typing import Iterable, Dict, Callable, List, Optional, Union, Tuple

from more_itertools import windowed, dotproduct, peekable
from pandas import date_range, Timedelta
from numpy import NaN

from ..._params import SourceSignalPair


def smoother(values: List[float], kernel: List[float] = None) -> float:
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

def pad_group(group: Iterable[Dict], pad_length: int, fill_value: Union[float, str] = NaN) -> Iterable[Dict]:
    """Prepend window with pad_length many fill values."""

    # Peek the first element for the date, fill value, and other data entries.
    group = peekable(group)
    start_entry = group.peek().copy()

    # Get the time bounds.
    right_bound = start_entry["timestamp"] - Timedelta(1, unit="D")
    left_bound = start_entry["timestamp"] - Timedelta(pad_length, unit="D")

    if isinstance(fill_value, str) and fill_value == "first":
        padded_values = (dict(ChainMap({"timestamp": date}, start_entry)) for date in date_range(left_bound, right_bound))
    elif isinstance(fill_value, str) and fill_value != "first":
        raise ValueError("String value of fill_value can only be 'first'.")
    elif isinstance(fill_value, float):
        padded_values = (dict(ChainMap({"timestamp": date, "value": fill_value}, start_entry)) for date in date_range(left_bound, right_bound))
    else:
        raise ValueError("fill_value should be a float or 'first'.")
    return chain(padded_values, group)

def generate_smooth_rows(
    rows: Iterable[Dict],
    smooth_values: Callable[[List[float]], float] = smoother,
    window_length: int = 7,
    pad_length: int = 6,
    fill_value: Optional[float] = None) -> Iterable[Dict]:
    """Generate smoothed row entries.

    There are roughly two modes of boundary handling:
    * no padding, the windows start at length 1 on the left boundary and grow to size
      window_length (achieved with fill_value = None)
    * value padding, window_length - 1 many fill_values are appended at the start of the
      given date (achieved with any other fill_value)

    Note that this function crucially relies on the assumption that the iterable rows
    has been pre-sorted by geo_value and by timestamp. If this assumption is violated,
    the results will likely be incoherent.

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
    fill_value: Optional[float], default None
        The value to use when padding. If None, then the initial windows are made dynamic like
        (group[0]), (group[0], group[1]), ..., (group[0], group[1], ..., group[smoothed_window_length]).
    """
    assert pad_length < window_length

    for _, group in groupby(rows, lambda row: (row["geo_type"], row["geo_value"])): # Iterable[Tuple[str, Iterable[Dict]]]
        group = pad_group(group, pad_length, fill_value) if fill_value is not None else pad_group(group, pad_length, NaN)
        for window in windowed(group, window_length): # Iterable[List[Dict]]
            smoothed_entry = window[-1].copy() # last timestamp of window
            if fill_value is not None:
                values = [entry["value"] for entry in window]
            else:
                values = [entry["value"] for entry in window if entry["value"] is not NaN]
            smoothed_entry["value"] = smooth_values(values)
            yield smoothed_entry

def generate_row_diffs(rows: Iterable[Dict], fill_value: Optional[Union[str, float]] = None) -> Iterable[Dict]:
    """Generate differences between row values.

    Note that this function crucially relies on the assumption that the iterable rows
    has been pre-sorted by geo_value and by timestamp. If this assumption is violated,
    the results will likely be incoherent.

    rows: Iterable[Dict]
        An iterable over the rows a database query returns. The rows are assumed to be
        dicts containing the "geo_type", "geo_value", and "timestamp" keys. Assumes the
        rows have been sorted by geo and timestamp beforehand.
    fill_value: Optional[Union[str, float]] or "first", default None
        The value used to prepend rows. If "first", then uses the first value of rows.
        If None, then no padding is used and the resulting iterable is shorter than the
        original by 1.
    """
    for _, group in groupby(rows, lambda row: (row["geo_type"], row["geo_value"])): # Iterable[Tuple[str, Iterable[Dict]]]
        group = pad_group(group, 1, fill_value) if fill_value is not None else group
        for window in windowed(group, 2):
            incidence_entry = window[-1].copy()
            incidence_entry["value"] = window[1]["value"] - window[0]["value"]
            yield incidence_entry

def generate_prop_signal(rows: Iterable[Dict], fill_value: Optional[Union[str, float]] = None) -> Iterable[Dict]:
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


"""
Which raw signals can be derived from another signal by means of differencing or smoothing?
Based on: https://docs.google.com/spreadsheets/d/1zb7ItJzY5oq1n-2xtvnPBiJu2L3AqmCKubrLkKJZVHs/edit#gid=329338228

google-symptoms	ageusia_raw_search	TRUE	ageusia_raw_search
google-symptoms	ageusia_raw_search	TRUE	ageusia_smoothed_search
google-symptoms	anosmia_raw_search	TRUE	anosmia_raw_search
google-symptoms	anosmia_raw_search	TRUE	anosmia_smoothed_search
google-symptoms	sum_anosmia_ageusia_raw_search sum_anosmia_ageusia_raw_search
google-symptoms	sum_anosmia_ageusia_raw_search sum_anosmia_ageusia_smoothed_search

jhu-csse	confirmed_incidence_num	TRUE	confirmed_incidence_num
jhu-csse	confirmed_incidence_num	TRUE	confirmed_7dav_cumulative_num
jhu-csse	confirmed_incidence_num	TRUE	confirmed_7dav_cumulative_prop
jhu-csse	confirmed_incidence_num	TRUE	confirmed_7dav_incidence_num
jhu-csse	confirmed_incidence_num	TRUE	confirmed_7dav_incidence_prop
jhu-csse	confirmed_incidence_num	TRUE	confirmed_cumulative_num
jhu-csse	confirmed_incidence_num	TRUE	confirmed_cumulative_prop
jhu-csse	confirmed_incidence_num	TRUE	confirmed_incidence_prop
jhu-csse	deaths_incidence_num	TRUE	deaths_incidence_num
jhu-csse	deaths_incidence_num	TRUE	deaths_7dav_cumulative_num
jhu-csse	deaths_incidence_num	TRUE	deaths_7dav_cumulative_prop
jhu-csse	deaths_incidence_num	TRUE	deaths_7dav_incidence_num
jhu-csse	deaths_incidence_num	TRUE	deaths_7dav_incidence_prop
jhu-csse	deaths_incidence_num	TRUE	deaths_cumulative_num
jhu-csse	deaths_incidence_num	TRUE	deaths_cumulative_prop
jhu-csse	deaths_incidence_num	TRUE	deaths_incidence_prop

usa-facts	confirmed_incidence_num	FALSE	confirmed_incidence_num
usa-facts	confirmed_incidence_num	TRUE	confirmed_7dav_cumulative_num
usa-facts	confirmed_incidence_num	TRUE	confirmed_7dav_cumulative_prop
usa-facts	confirmed_incidence_num	FALSE	confirmed_7dav_incidence_num
usa-facts	confirmed_incidence_num	FALSE	confirmed_7dav_incidence_prop
usa-facts	confirmed_incidence_num	FALSE	confirmed_cumulative_num
usa-facts	confirmed_incidence_num	FALSE	confirmed_cumulative_prop
usa-facts	confirmed_incidence_num	FALSE	confirmed_incidence_prop
usa-facts	deaths_incidence_num	FALSE	deaths_incidence_num
usa-facts	deaths_incidence_num	TRUE	deaths_7dav_cumulative_num
usa-facts	deaths_incidence_num	TRUE	deaths_7dav_cumulative_prop
usa-facts	deaths_incidence_num	FALSE	deaths_7dav_incidence_num
usa-facts	deaths_incidence_num	FALSE	deaths_7dav_incidence_prop
usa-facts	deaths_incidence_num	FALSE	deaths_cumulative_num
usa-facts	deaths_incidence_num	FALSE	deaths_cumulative_prop
usa-facts	deaths_incidence_num	FALSE	deaths_incidence_prop
"""

IDENTITY = lambda rows: rows
DIFF = lambda rows: generate_row_diffs(rows)
SMOOTH = lambda rows: generate_smooth_rows(rows)
DIFF_SMOOTH = lambda rows: generate_smooth_rows(generate_row_diffs(rows))

DERIVED_SIGNALS = {
    "google-symptoms:ageusia_smoothed_search": ("google-symptoms:ageusia_raw_search", SMOOTH),
    "google-symptoms:anosmia_smoothed_search": ("google-symptoms:anosmia_raw_search", SMOOTH),
    "google-symptoms:sum_anosmia_ageusia_smoothed_search": ("google-symptoms:sum_anosmia_ageusia_raw_search", SMOOTH),
    "jhu-csse:confirmed_7dav_cumulative_num": ("jhu-csse:confirmed_cumulative_num", SMOOTH),
    "jhu-csse:confirmed_7dav_incidence_num": ("jhu-csse:confirmed_cumulative_num", DIFF_SMOOTH),
    "jhu-csse:confirmed_incidence_num": ("jhu-csse:confirmed_cumulative_num", DIFF),
    "jhu-csse:deaths_7dav_cumulative_num": ("jhu-csse:deaths_cumulative_num", SMOOTH),
    "jhu-csse:deaths_7dav_incidence_num": ("jhu-csse:deaths_cumulative_num", DIFF_SMOOTH),
    "jhu-csse:deaths_incidence_num": ("jhu-csse:deaths_cumulative_num", DIFF),
    "usafacts:confirmed_7dav_cumulative_num": ("usafacts:confirmed_cumulative_num", SMOOTH),
    "usafacts:confirmed_7dav_incidence_num": ("usafacts:confirmed_cumulative_num", DIFF_SMOOTH),
    "usafacts:confirmed_incidence_num": ("usafacts:confirmed_cumulative_num", DIFF),
    "usafacts:deaths_7dav_cumulative_num": ("usafacts:deaths_cumulative_num", SMOOTH),
    "usafacts:deaths_7dav_incidence_num": ("usafacts:deaths_cumulative_num", DIFF_SMOOTH),
    "usafacts:deaths_incidence_num": ("usafacts:deaths_cumulative_num", DIFF),
}

def fetch_derivable_signal(source_signal_pair: SourceSignalPair) -> Tuple[SourceSignalPair, Callable]:
    """Fetch raw version of a signal, if available, for smoothing."""
    source_signal_name = source_signal_pair.source + ":" + source_signal_pair.signal
    try:
        raw_source_signal, transform = DERIVED_SIGNALS[source_signal_name]
        raw_source, raw_signal = raw_source_signal.split(":")
        return SourceSignalPair(raw_source, raw_signal), transform
    except KeyError:
        return source_signal_pair, IDENTITY

def fetch_derivable_signals(source_signal_pairs: List[SourceSignalPair]) -> Dict[str, Tuple[SourceSignalPair, Callable]]:
    signals_and_transforms = [fetch_derivable_signal(source_signal_pair) for source_signal_pair in source_signal_pairs]
    signals_and_transforms_dict = {source_signal_pair.source + ":" + source_signal_pair.signal: transform for source_signal_pair, transform in signals_and_transforms}
    return signals_and_transforms_dict
