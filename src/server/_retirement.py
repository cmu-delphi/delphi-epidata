"""
Guards for data this API no longer provides.

See the retirement block in `_config.py`: nothing with a time value after the cutoff is produced
here anymore, so a request asking *only* for times beyond the cutoff can never be satisfied. Rather
than returning an empty result set (which looks like "no data for that query"), we fail it loudly
with `DataRetiredException` so users of the old API learn where to go instead.

Requests that straddle the cutoff are served normally -- clients polling with open-ended ranges
(e.g. `time_values=20200101-20301231` or `*`) keep working and get the deprecation headers added in
`_common.after_request_execute`.
"""

from typing import Optional, Sequence, Union

from ._config import RETIREMENT_CUTOFF_DAY, RETIREMENT_CUTOFF_WEEK
from ._exceptions import DataRetiredException
from .utils import IntRange, guess_time_value_is_week

# request parameters that hold time values. all parsers check only these.
# counts (`lag`, `hours`, `weeks`, ...) are not time values.
# `latest` is the end of a window that can include servable days, so it is not checked.
# `as_of` after the cutoff selects the same data as no `as_of`, but it is rejected on purpose: a
# request for a version after the cutoff gets the retirement message.
TIME_PARAM_KEYS = frozenset(
    {
        "epiweeks",
        "dates",
        "time_values",
        "issues",
        "publication_dates",
        "collection_weeks",
        "as_of",
        "basis",
        "date",
        "start_day",
        "end_day",
        "window",
        "time",
    }
)


def is_time_param(key: Union[str, Sequence[str]]) -> bool:
    """
    whether the given request parameter name (or tuple of aliases) holds time values
    """
    if isinstance(key, str):
        return key in TIME_PARAM_KEYS
    return any(k in TIME_PARAM_KEYS for k in key)


def _is_retired(value: IntRange, time_type: Optional[str]) -> bool:
    """
    whether this single time value / range lies entirely after the retirement cutoff
    """
    if not isinstance(value, (int, tuple)):
        # the "*" wildcard and anything else unbounded: not something we can rule out
        return False
    start = value[0] if isinstance(value, tuple) else value
    if time_type == "week" or (time_type is None and guess_time_value_is_week(start)):
        return start > RETIREMENT_CUTOFF_WEEK
    return start > RETIREMENT_CUTOFF_DAY


def require_servable_times(
    key: Union[str, Sequence[str]],
    values: Union[bool, IntRange, Sequence[IntRange], None],
    time_type: Optional[str] = None,
) -> None:
    """
    raises DataRetiredException if every requested time value lies after the retirement cutoff.

    `time_type` is "day"/"week" when the caller knows it, otherwise it is guessed per value from
    the number of digits. `values` may be a single value, a (start, end) range, a list of either, or
    True/None for "everything" -- the latter is never retired, since it also covers servable times.
    """
    if values is None or isinstance(values, bool):
        return
    items = values if isinstance(values, list) else [values]
    if not items:
        return
    if all(_is_retired(value, time_type) for value in items):
        name = key if isinstance(key, str) else "/".join(key)
        raise DataRetiredException(f"{name} is entirely after the cutoff")
