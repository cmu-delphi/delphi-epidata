from enum import Enum
from logging import getLogger
from numbers import Number
from typing import Iterable, Dict, List, Union

from more_itertools import windowed
from numpy import nan, array, dot, isnan, nan_to_num, ndarray

from delphi_utils.nancodes import Nans

from ...utils.dates import time_value_to_date


class SmootherKernelValue(str, Enum):
    average = "average"


def generate_smoothed_rows(
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
        Either a SmootherKernelValue or a custom list of numbers for weighted averaging.
    smoother_window_length: int, default 7
        The length of the averaging window for the smoother.
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
        # This occurs only if len(rows) < smoother_window_length.
        if None in window:
            continue

        new_value = _smoother(_get_validated_window_values(window, nan_fill_value), kernel=smoother_kernel)
        # The database returns NULL values as None, so we stay consistent with that.
        new_value = float(round(new_value, 7)) if not isnan(new_value) else None
        if new_value and isnan(new_value):
            breakpoint()

        new_item = _fill_remaining_row_values(window)
        new_item.update({"value": new_value, "missing_value": Nans.NOT_MISSING if new_value is not None else Nans.NOT_APPLICABLE})

        yield new_item


def generate_diffed_rows(rows: Iterable[Dict], nan_fill_value: Number = nan, **kwargs) -> Iterable[Dict]:
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
    if not isinstance(nan_fill_value, Number):
        nan_fill_value = nan

    for window in windowed(rows, 2):
        # This occurs only if len(rows) < 2.
        if None in window:
            continue 

        first_value, second_value = _get_validated_window_values(window, nan_fill_value)
        new_value = round(second_value - first_value, 7)
        # The database returns NULL values as None, so we stay consistent with that.
        new_value = float(new_value) if not isnan(new_value) else None

        new_item = _fill_remaining_row_values(window)
        new_item.update({"value": new_value, "missing_value": Nans.NOT_MISSING if new_value is not None else Nans.NOT_APPLICABLE})

        yield new_item


def _smoother(values: List[Number], kernel: Union[List[Number], SmootherKernelValue] = SmootherKernelValue.average) -> Number:
    """Basic smoother.

    If kernel passed, uses the kernel as summation weights. If something is wrong,
    defaults to the mean.
    """

    if kernel and isinstance(kernel, list):
        kernel = array(kernel, copy=False)
        values = array(values, copy=False)
        smoothed_value = dot(values, kernel)
    elif kernel and isinstance(kernel, SmootherKernelValue):
        if kernel == SmootherKernelValue.average:
            smoothed_value = array(values).mean()
        else:
            raise ValueError("Unimplemented SmootherKernelValue.")
    else:
        raise ValueError("Kernel must be specified in _smoother.")

    return smoothed_value


def _get_validated_window_values(window: List[dict], nan_fill_value: Number) -> ndarray:
    """Extracts and validates the values in the window, returning a list of floats.

    The main objective is to create a consistent nan type values from None or np.nan. We replace None with np.nan, so they can be filled.

    Assumes any None values were filtered out of window, so it is a list of Dict only.
    """
    return nan_to_num([e.get("value") if e.get("value") is not None else nan for e in window], nan=nan_fill_value)


def _fill_remaining_row_values(window: Iterable[dict]) -> dict:
    """Set a few default fields for the covidcast row."""
    logger = getLogger("gunicorn.error")

    # Start by defaulting to the field values of the last window member.
    new_item = window[-1].copy()

    try:
        issues = [e.get("issue") for e in window]
        if None in issues:
            new_issue = None
        else:
            new_issue = max(issues)
    except (TypeError, ValueError):
        logger.warn(f"There was an error computing an issue field for {new_item.get('source')}:{new_item.get('signal')}.")
        new_issue = None

    try:
        if new_issue is None:
            new_lag = None
        else:
            new_lag = (time_value_to_date(new_issue) - time_value_to_date(new_item["time_value"])).days
    except (TypeError, ValueError):
        logger.warn(f"There was an error computing a lag field for {new_item.get('source')}:{new_item.get('signal')}.")
        new_lag = None

    new_item.update({
        "issue": new_issue,
        "lag": new_lag,
        "stderr": None,
        "sample_size": None,
        "missing_stderr": Nans.NOT_APPLICABLE,
        "missing_sample_size": Nans.NOT_APPLICABLE
    })

    return new_item
