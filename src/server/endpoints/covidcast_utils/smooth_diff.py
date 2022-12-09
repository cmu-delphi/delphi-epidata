import itertools
from enum import Enum
from logging import getLogger
from numbers import Number
from typing import Dict, Iterable, List

import numpy as np
from delphi_utils.nancodes import Nans

from ...utils.dates import time_value_to_day


def windowed(iterable, n):
    it = iter(iterable)
    result = tuple(itertools.islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


class SmootherKernelValue(str, Enum):
    average = "average"


def generate_smoothed_rows(
    rows: Iterable[Dict],
    smoother_window_length: int = 7,
    nan_fill_value: Number = np.nan,
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
    smoother_window_length: int, default 7
        The length of the averaging window for the smoother.
    nan_fill_value: Number, default nan
        The value to use when encountering nans (e.g. None and numpy.nan types); uses nan by default.
    **kwargs:
        Container for non-shared parameters with other computation functions.
    """
    # Validate params.
    if not isinstance(smoother_window_length, int) or smoother_window_length < 1:
        smoother_window_length = 7
    if not isinstance(nan_fill_value, Number):
        nan_fill_value = np.nan

    for window in windowed(rows, smoother_window_length):  # Iterable[List[Dict]]
        new_value = 0
        for row in window:
            if row.get("value") is not None:
                new_value += row["value"]
            else:
                new_value += nan_fill_value
        new_value /= smoother_window_length
        new_value = float(round(new_value, 7)) if not np.isnan(new_value) else None

        new_item = _fill_remaining_row_fields(window)
        new_item.update({"value": new_value, "missing_value": Nans.NOT_MISSING if new_value is not None else Nans.NOT_APPLICABLE})

        yield new_item


def generate_diffed_rows(rows: Iterable[Dict], nan_fill_value: Number = np.nan, **kwargs) -> Iterable[Dict]:
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
        nan_fill_value = np.nan

    for window in windowed(rows, 2):
        first_value = window[0]["value"] if window[0].get("value") is not None else nan_fill_value
        second_value = window[1]["value"] if window[1].get("value") is not None else nan_fill_value
        new_value = float(round(second_value - first_value, 7))
        new_value = new_value if not np.isnan(new_value) else None

        new_item = _fill_remaining_row_fields(window)
        new_item.update({"value": new_value, "missing_value": Nans.NOT_MISSING if new_value is not None else Nans.NOT_APPLICABLE})

        yield new_item


def _fill_remaining_row_fields(window: List[dict]) -> dict:
    """Set a few default fields for the covidcast row."""
    logger = getLogger("gunicorn.error")

    # Start by defaulting to the field values of the last window member.
    new_item = window[-1].copy()

    try:
        new_issue = max(e.get("issue") for e in window if e.get("issue") is not None)
    except (TypeError, ValueError):
        logger.warn(f"There was an error computing an issue field for {new_item.get('source')}:{new_item.get('signal')}, geo: {new_item.get('geo_value')}, date: {new_item.get('time_value')}.")
        new_issue = None

    try:
        new_lag = (time_value_to_day(new_issue) - time_value_to_day(new_item["time_value"])).days
    except (TypeError, ValueError):
        logger.warn(f"There was an error computing a lag field for {new_item.get('source')}:{new_item.get('signal')}, geo: {new_item.get('geo_value')}, date: {new_item.get('time_value')}.")
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
