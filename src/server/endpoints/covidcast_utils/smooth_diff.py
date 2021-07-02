from collections import ChainMap
from itertools import groupby, chain
from typing import Iterable, Dict, List, Optional, Union

from more_itertools import windowed, peekable
from pandas import date_range, Timedelta
from numpy import nan, nan_to_num, array, dot, isnan


def _smoother(values: List[float], kernel: Optional[List[float]] = None) -> float:
    """Basic smoother.

    If kernel passed, uses the kernel as summation weights. If something is wrong,
    defaults to the mean.
    """
    try:
        if kernel:
            kernel = array(kernel, dtype=float, copy=False)
        else:
            raise ValueError
        values = array(values, dtype=float, copy=False)
        smoothed_value = dot(values, kernel)
    except (ValueError, TypeError):
        smoothed_value = array(values).mean()

    return smoothed_value


def _pad_group(group: Iterable[Dict], pad_length: int, pad_fill_value: Union[float, str] = nan) -> Iterable[Dict]:
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


def generate_smooth_rows(
    rows: Iterable[Dict],
    smoother_kernel: Union[str, List[float]] = "average",
    window_length: int = 7,
    pad_length: int = 6,
    pad_fill_value: Optional[Union[str, float]] = "drop",
    nan_fill_value: float = nan,
) -> Iterable[Dict]:
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
    smooth_kernel: List[float], "average", default "average"
        A function taking a list of floats and producing a smoothed value. The smoothed
        value is placed in the timestamp of the last entry in the list of floats.
    window_length: int, default 7
        The smoothing window for length for the smoother.
    pad_length: int, default 6
        Number of fill_value values to prepend to each group. Set to window_length-1
        to get a value for each timestamp in rows. This helps generates a slide into an iterable's
        items. Assumed to be less than window_length.
    pad_fill_value: float, "first", default "drop"
        The value to use when padding. If None, then the initial windows are made dynamic like
        (group[0]), (group[0], group[1]), ..., (group[0], group[1], ..., group[smoothed_window_length]).
        If "first", then the value from the first entry is used for filling.
    nan_fill_value: float, default 0.
        The value to use when encountering nans. By default, conforms None and numpy.nan types to numpy.nan.
        This will propagate nans. Otherwise, uses a float value.
    """
    # Validate params.
    if not isinstance(window_length, int) or (isinstance(window_length, int) and window_length < 1):
        window_length = 7
    if not isinstance(pad_length, int) or (isinstance(pad_length, int) and pad_length >= window_length):
        pad_length = window_length - 1
    if not isinstance(nan_fill_value, (float, int)):
        nan_fill_value = 0.
    if not isinstance(pad_fill_value, (float, int, str)) or (isinstance(pad_fill_value, str) and pad_fill_value not in ["first", "drop"]):
        pad_fill_value = "drop"
    if not isinstance(smoother_kernel, list) or (isinstance(smoother_kernel, str) and smoother_kernel != "average"):
        smoother_kernel = "average"

    for key, group in groupby(rows, lambda row: (row["geo_type"], row["geo_value"])):  # Iterable[Tuple[str, Iterable[Dict]]]
        group = _pad_group(group, pad_length, pad_fill_value)
        for window in windowed(group, window_length):  # Iterable[List[Dict]]
            smoothed_entry = window[-1].copy()  # inherit the values of the last timestamp of window

            if pad_fill_value == "drop":
                values = [entry["value"] for entry in window if entry["value"] != "drop"]
            else:
                values = [entry["value"] for entry in window]
            values = nan_to_num(array(values, dtype=float), nan=nan_fill_value)

            if smoother_kernel == "average":
                smoothed_value = values.mean()
            if isinstance(smoother_kernel, list):
                smoothed_value = _smoother(values, smoother_kernel)

            smoothed_entry["value"] = smoothed_value if not isnan(smoothed_value) else None
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
    if not isinstance(pad_fill_value, (float, str, type(None))) or (isinstance(pad_fill_value, str) and pad_fill_value != "first"):
        pad_fill_value = "first"

    for _, group in groupby(rows, lambda row: (row["geo_type"], row["geo_value"])):  # Iterable[Tuple[str, Iterable[Dict]]]
        group = _pad_group(group, 1, pad_fill_value) if pad_fill_value is not None else group
        for window in windowed(group, 2):
            incidence_entry = window[-1].copy()
            incidence_entry["value"] = window[1]["value"] - window[0]["value"]
            yield incidence_entry
