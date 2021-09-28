from enum import Enum
from numbers import Number
from typing import Iterable, Dict, List, Optional, Union

from more_itertools import windowed
from numpy import nan, nan_to_num, array, dot, isnan


class PadFillValue(str, Enum):
    first = "first"
    drop = "drop"
    none = "none"


class SmootherKernelValue(str, Enum):
    average = "average"




def generate_smooth_rows(
    rows: Iterable[Dict],
    smoother_kernel: Union[List[Number], SmootherKernelValue] = SmootherKernelValue.average,
    smoother_window_length: int = 7,
    nan_fill_value: Number = nan,
    **kwargs
) -> Iterable[Dict]:
    """Generate smoothed row entries.

    There are roughly two modes of boundary handling:
    * no padding, the windows start at length 1 on the left boundary and grow to size
      smoother_window_length (achieved with pad_fill_value = None)
    * value padding, smoother_window_length - 1 many fill_values are appended at the start of the
      given date (achieved with any other pad_fill_value)

    Note that this function crucially relies on the assumption that the iterable rows
    have been sorted by time_value. If this assumption is violated, the results will likely be
    incoherent.

    Parameters
    ----------
    rows: Iterable[Dict]
        An iterable over the rows a database query returns. The rows are assumed to be
        dicts containing the "geo_type", "geo_value", and "time_value" keys. Assumes the
        rows have been sorted by geo and time_value beforehand.
    smooth_kernel: Union[List[Number], SmootherKernelValue], default SmootherValue.average
        A list of numbers used as weights for averaging.
    smoother_window_length: int, default 7
        The smoothing window for length for the smoother.
    nan_fill_value: Number, default nan
        The value to use when encountering nans (e.g. None and numpy.nan types); uses nan by default.
    **kwargs:
        Container for non-shared parameters with other computation functions.
    """
    for window in windowed(rows, smoother_window_length):
        yield smoothed_row(window)


def generate_row_diffs(rows: Iterable[Dict], nan_fill_value: Number = nan, **kwargs) -> Iterable[Dict]:
    """Generate differences between row values.

    Note that this function crucially relies on the assumption that the iterable rows have been
    sorted by time_value. If this assumption is violated, the results will likely be incoherent.

    rows: Iterable[Dict]
        An iterable over the rows a database query returns. The rows are assumed to be dicts
        containing the "geo_type", "geo_value", and "time_value" keys. Assumes the rows have been
        sorted by geo and time_value beforehand.
    nan_fill_value: Number, default nan
        The value to use when encountering nans (e.g. None and numpy.nan types); uses nan by default.
    **kwargs:
        Container for non-shared parameters with other computation functions.
    """
    for window in windowed(rows, 2):
        if all(e is None for e in window):
            continue # should only occur if rows is empty
        try:
            first_value = window[0].get("value", nan_fill_value) if window[0] is not None else nan_fill_value
            second_value = window[1].get("value", nan_fill_value) if window[1] is not None else nan_fill_value
            value = round(second_value - first_value, 8)
            value = float(value) if not isnan(value) else None
        except TypeError:
            value = None
        item = list(filter(lambda e: e is not None, window))[-1].copy() # inherit values of last time stamp
        item.update({"value": value, "stderr": None, "sample_size": None, "missing_value": Nans.NOT_MISSING if value is not None else Nans.NOT_APPLICABLE, "missing_stderr": Nans.NOT_APPLICABLE, "missing_sample_size": Nans.NOT_APPLICABLE})
        yield item
