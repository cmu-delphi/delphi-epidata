"""Provides unified not-a-number codes for the indicators.

Currently requires a manual sync between the covidcast-indicators
and the delphi-epidata repo.
* in covidcast-indicators: _delphi_utils_python/delphi_utils
* in delphi-epidata: src/acquisition/covidcast
"""

from enum import IntEnum

class Nans(IntEnum):
    """An enum of not-a-number codes for the indicators."""

    NOT_MISSING = 0
    NOT_APPLICABLE = 1
    REGION_EXCEPTION = 2
    PRIVACY = 3
    DELETED = 4
    UNKNOWN = 5
