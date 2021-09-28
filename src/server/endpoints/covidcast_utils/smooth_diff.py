from enum import Enum
from numbers import Number
from typing import Iterable, Dict, List, Optional, Union

from more_itertools import windowed
from numpy import nan, nan_to_num, array, dot, isnan

from delphi_utils.nancodes import Nans

class PadFillValue(str, Enum):
    first = "first"
    drop = "drop"
    none = "none"


class SmootherKernelValue(str, Enum):
    average = "average"


def _smoother(values: List[Number], kernel: Optional[Union[List[Number], SmootherKernelValue]] = None) -> Number:
    """Basic smoother.

    If kernel passed, uses the kernel as summation weights. If something is wrong,
    defaults to the mean.
    """
    try:
        if kernel and isinstance(kernel, list):
            kernel = array(kernel, copy=False)
            values = array(values, copy=False)
            smoothed_value = dot(values, kernel)
            return smoothed_value
        else:
            raise ValueError
    except (ValueError, TypeError):
        try:
            smoothed_value = array(values).mean()
        except (ValueError, TypeError):
            smoothed_value = None

    return smoothed_value


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
    # Validate params.
    if not isinstance(smoother_window_length, int) or (isinstance(smoother_window_length, int) and smoother_window_length < 1):
        smoother_window_length = 7
    if isinstance(smoother_kernel, list):
        smoother_window_length = len(smoother_kernel)
    if not isinstance(nan_fill_value, Number):
        nan_fill_value = nan
    if not isinstance(smoother_kernel, (list, SmootherKernelValue)):
        smoother_kernel = SmootherKernelValue.average

    for window in windowed(rows, smoother_window_length):  # Iterable[List[Dict]]
        if all(e is None for e in window):
            continue
        value = _smoother(nan_to_num([e.get("value") if e else nan_fill_value for e in window], nan=nan_fill_value), smoother_kernel)
        value = float(round(value, 8)) if value and not isnan(value) else None
        last_item = list(filter(lambda e: e is not None, window))[-1]
        item = last_item.copy() # inherit values of last time stamp
        item.update({"value": value, "stderr": None, "sample_size": None, "missing_value": Nans.NOT_MISSING if value is not None else Nans.NOT_APPLICABLE, "missing_stderr": Nans.NOT_APPLICABLE, "missing_sample_size": Nans.NOT_APPLICABLE})
        yield item


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
