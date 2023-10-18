from math import inf
import re
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple, Union
import delphi_utils

from flask import request


from ._exceptions import ValidationFailedException
from .utils import days_in_range, weeks_in_range, guess_time_value_is_day, guess_time_value_is_week, IntRange, TimeValues, days_to_ranges, weeks_to_ranges
from ._validate import require_any, require_all


def _parse_common_multi_arg(key: str) -> List[Tuple[str, Union[bool, Sequence[str]]]]:
    # support multiple request parameter with the same name
    line = ";".join(request.values.getlist(key))

    parsed: List[Tuple[str, Union[bool, Sequence[str]]]] = []

    if not line:
        return parsed

    pattern: re.Pattern[str] = re.compile(r"^([\w\-_]+):(.*)$", re.MULTILINE)
    for entry in line.split(";"):
        m: Optional[re.Match[str]] = pattern.match(entry)
        if not m:
            raise ValidationFailedException(f"{key} param: {entry} is not matching <{key}_type>:<{key}_values> syntax")
        group_type: str = m.group(1).strip().lower()
        group_value: str = m.group(2).strip().lower()
        if group_value == "*":
            parsed.append((group_type, True))
        else:
            parsed.append((group_type, [g.strip() for g in group_value.split(",")]))
    return parsed


def _parse_single_arg(key: str) -> Tuple[str, str]:
    """
    parses a single pair
    """
    v = request.values.get(key)
    if not v:
        raise ValidationFailedException(f"{key} param is required")
    pattern: re.Pattern[str] = re.compile(r"^([\w\-_]+):([\w\-_]+)$", re.MULTILINE)
    m: Optional[re.Match[str]] = pattern.match(v)
    if not v or not m:
        raise ValidationFailedException(f"{key} param: is not matching <{key}_type>:<{key}_value> syntax")
    return m.group(1).strip().lower(), m.group(2).strip().lower()


@dataclass
class GeoSet:
    geo_type: str
    geo_values: Union[bool, Sequence[str]]

    def __init__(self, geo_type: str, geo_values: Union[bool, Sequence[str]]):
        if not isinstance(geo_values, bool):
            if geo_values == ['']:
                raise ValidationFailedException(f"geo_value is empty for the requested geo_type {geo_type}!")
            # TODO: keep this translator in sync with CsvImporter.GEOGRAPHIC_RESOLUTIONS in acquisition/covidcast/ and with GeoMapper
            geo_type_translator = {
                "county": "fips",
                "state": "state_id",
                "zip": "zip",
                "hrr": "hrr",
                "hhs": "hhs",
                "msa": "msa",
                "nation": "nation"
            }
            if geo_type in geo_type_translator: # else geo_type is unknown to GeoMapper
                allowed_values = delphi_utils.geomap.GeoMapper().get_geo_values(geo_type_translator[geo_type])
                invalid_values = set(geo_values) - set(allowed_values)
                if invalid_values:
                    raise ValidationFailedException(f"Invalid geo_value(s) {', '.join(invalid_values)} for the requested geo_type {geo_type}")
        self.geo_type = geo_type
        self.geo_values = geo_values

    def matches(self, geo_type: str, geo_value: str) -> bool:
        return self.geo_type == geo_type and (self.geo_values is True or (not isinstance(self.geo_values, bool) and geo_value in self.geo_values))

    def count(self) -> float:
        """
        returns the count of items in this set
        """
        if isinstance(self.geo_values, bool):
            return inf if self.geo_values else 0
        return len(self.geo_values)


def parse_geo_arg(key: str = "geo") -> List[GeoSet]:
    return [GeoSet(geo_type, geo_values) for [geo_type, geo_values] in _parse_common_multi_arg(key)]


def parse_single_geo_arg(key: str) -> GeoSet:
    """
    parses a single geo set with only one value
    """
    r = _parse_single_arg(key)
    return GeoSet(r[0], [r[1]])


@dataclass
class SourceSignalSet:
    source: str
    signal: Union[bool, Sequence[str]]

    def matches(self, source: str, signal: str) -> bool:
        return self.source == source and (self.signal is True or (not isinstance(self.signal, bool) and signal in self.signal))

    def count(self) -> float:
        """
        returns the count of items in this set
        """
        if isinstance(self.signal, bool):
            return inf if self.signal else 0
        return len(self.signal)


def parse_source_signal_arg(key: str = "signal") -> List[SourceSignalSet]:
    return [SourceSignalSet(source, signals) for [source, signals] in _parse_common_multi_arg(key)]


def parse_single_source_signal_arg(key: str) -> SourceSignalSet:
    """
    parses a single source signal set with only one value
    """
    r = _parse_single_arg(key)
    return SourceSignalSet(r[0], [r[1]])


@dataclass
class TimeSet:
    time_type: str
    time_values: Union[bool, TimeValues]

    @property
    def is_week(self) -> bool:
        return self.time_type == 'week'

    @property
    def is_day(self) -> bool:
        return self.time_type != 'week'


    def count(self) -> float:
        """
        returns the count of items in this set
        """
        if isinstance(self.time_values, bool):
            return inf if self.time_values else 0
        if self.time_type == 'week':
            return sum(1 if isinstance(v, int) else weeks_in_range(v) for v in self.time_values)
        return sum(1 if isinstance(v, int) else days_in_range(v) for v in self.time_values)

    def to_ranges(self):
        """
        returns this set with times converted to ranges
        """
        if isinstance(self.time_values, bool):
            return TimeSet(self.time_type, self.time_values)
        if self.time_type == 'week':
            return TimeSet(self.time_type, weeks_to_ranges(self.time_values))
        return TimeSet(self.time_type, days_to_ranges(self.time_values))


def _verify_range(start: int, end: int) -> IntRange:
    if start == end:
        # the first and last numbers are the same, just treat it as a singe value
        return start
    elif end > start:
        # add the range as an array
        return (start, end)
    # the range is inverted, this is an error
    raise ValidationFailedException(f"the given range {start}-{end} is inverted")


def parse_week_value(time_value: str) -> IntRange:
    count_dashes = time_value.count("-")
    msg = f"{time_value} does not match a known format YYYYWW or YYYYWW-YYYYWW"

    if count_dashes == 0:
        # plain delphi date YYYYWW
        if not re.match(r"^(\d{6})$", time_value, re.MULTILINE):
            raise ValidationFailedException(msg)
        return int(time_value)

    if count_dashes == 1:
        # delphi date range YYYYWW-YYYYWW
        if not re.match(r"^(\d{6})-(\d{6})$", time_value, re.MULTILINE):
            raise ValidationFailedException(msg)
        [first, last] = time_value.split("-", 2)
        return _verify_range(int(first), int(last))

    raise ValidationFailedException(msg)


def parse_day_value(time_value: str) -> IntRange:
    count_dashes = time_value.count("-")
    msg = f"{time_value} does not match a known format YYYYMMDD, YYYY-MM-DD, YYYYMMDD-YYYYMMDD, or YYYY-MM-DD--YYYY-MM-DD"

    if count_dashes == 0:
        # plain delphi date YYYYMMDD
        if not re.match(r"^(\d{8})$", time_value, re.MULTILINE):
            raise ValidationFailedException(msg)
        return int(time_value)

    if count_dashes == 2:
        # iso date YYYY-MM-DD
        if not re.match(r"^(\d{4}-\d{2}-\d{2})$", time_value, re.MULTILINE):
            raise ValidationFailedException(msg)
        return int(time_value.replace("-", ""))

    if count_dashes == 1:
        # delphi date range YYYYMMDD-YYYYMMDD
        if not re.match(r"^(\d{8})-(\d{8})$", time_value, re.MULTILINE):
            raise ValidationFailedException(msg)
        [first, last] = time_value.split("-", 2)
        return _verify_range(int(first), int(last))

    if count_dashes == 6:
        # delphi iso date range YYYY-MM-DD--YYYY-MM-DD
        if not re.match(r"^(\d{4}-\d{2}-\d{2})--(\d{4}-\d{2}-\d{2})$", time_value, re.MULTILINE):
            raise ValidationFailedException(msg)
        [first, last] = time_value.split("--", 2)
        return _verify_range(int(first.replace("-", "")), int(last.replace("-", "")))

    raise ValidationFailedException(msg)


def _parse_time_set(time_type: str, time_values: Union[bool, Sequence[str]]) -> TimeSet:
    if isinstance(time_values, bool):
        return TimeSet(time_type, time_values)

    if time_type == "week":
        return TimeSet("week", [parse_week_value(t) for t in time_values])
    elif time_type == "day":
        return TimeSet("day", [parse_day_value(t) for t in time_values])
    raise ValidationFailedException(f'time param: {time_type} is not one of "day" or "week"')


def parse_time_arg(key: str = "time") -> Optional[TimeSet]:
    time_sets = [_parse_time_set(time_type, time_values) for [time_type, time_values] in _parse_common_multi_arg(key)]

    # single value
    if len(time_sets) == 0:
        return None
    if len(time_sets) == 1:
        return time_sets[0]

    # make sure 'day' and 'week' aren't mixed
    time_types = set(time_set.time_type for time_set in time_sets)
    if len(time_types) >= 2:
        raise ValidationFailedException(f'{key}: {time_sets} mixes "day" and "week" time types')

    # merge all time sets into one
    merged = []
    for time_set in time_sets:
        if time_set.time_values is True:
            return time_set
        else:
            merged.extend(time_set.time_values)
    return TimeSet(time_sets[0].time_type, merged).to_ranges()


def parse_single_time_arg(key: str) -> TimeSet:
    """
    parses a single time set with only one value
    """
    r = _parse_single_arg(key)
    return _parse_time_set(r[0], [r[1]])


def parse_day_range_arg(key: str) -> Tuple[int, int]:
    v = request.values.get(key)
    if not v:
        raise ValidationFailedException(f"{key} param is required")
    r = parse_day_value(v)
    if not isinstance(r, tuple):
        raise ValidationFailedException(f"{key} must match YYYYMMDD-YYYYMMDD or YYYY-MM-DD--YYYY-MM-DD")
    return r


def parse_day_arg(key: str) -> int:
    v = request.values.get(key)
    if not v:
        raise ValidationFailedException(f"{key} param is required")
    r = parse_day_value(v)
    if not isinstance(r, int):
        raise ValidationFailedException(f"{key} must match YYYYMMDD or YYYY-MM-DD")
    return r

def parse_week_arg(key: str) -> int:
    v = request.values.get(key)
    if not v:
        raise ValidationFailedException(f"{key} param is required")
    r = parse_week_value(v)
    if not isinstance(r, int):
        raise ValidationFailedException(f"{key} must match YYYYWW")
    return r


def parse_week_range_arg(key: str) -> Tuple[int, int]:
    v = request.values.get(key)
    if not v:
        raise ValidationFailedException(f"{key} param is required")
    r = parse_week_value(v)
    if not isinstance(r, tuple):
        raise ValidationFailedException(f"{key} must match YYYYWW-YYYYWW")
    return r

def parse_day_or_week_arg(key: str, default_value: Optional[int] = None) -> TimeSet:
    v = request.values.get(key)
    if not v:
        if default_value is not None:
            time_type = "day" if guess_time_value_is_day(default_value) else "week"
            return TimeSet(time_type, [default_value])
        raise ValidationFailedException(f"{key} param is required")
    # format is either YYYY-MM-DD or YYYYMMDD or YYYYMM
    is_week = guess_time_value_is_week(v)
    if is_week:
        return TimeSet("week", [parse_week_arg(key)])
    return TimeSet("day", [parse_day_arg(key)])

def parse_day_or_week_range_arg(key: str) -> TimeSet:
    v = request.values.get(key)
    if not v:
        raise ValidationFailedException(f"{key} param is required")
    # format is either YYYY-MM-DD--YYYY-MM-DD or YYYYMMDD-YYYYMMDD or YYYYMM-YYYYMM
    # so if the first before the - has length 6, it must be a week
    is_week = guess_time_value_is_week(v.split('-', 2)[0])
    if is_week:
        return TimeSet("week", [parse_week_range_arg(key)])
    return TimeSet("day", [parse_day_range_arg(key)])


def _extract_value(key: Union[str, Sequence[str]]) -> Optional[str]:
    if isinstance(key, str):
        return request.values.get(key)
    for k in key:
        if k in request.values:
            return request.values[k]
    return None


def _extract_list_value(key: Union[str, Sequence[str]]) -> List[str]:
    if isinstance(key, str):
        return request.values.getlist(key)
    for k in key:
        if k in request.values:
            return request.values.getlist(k)
    return []


def extract_strings(key: Union[str, Sequence[str]]) -> Optional[List[str]]:
    s = _extract_list_value(key)
    if not s:
        # nothing to do
        return None
    # we can have multiple values
    return [v for vs in s for v in vs.split(",")]


def extract_integer(key: Union[str, Sequence[str]]) -> Optional[int]:
    s = _extract_value(key)
    if not s:
        # nothing to do
        return None
    try:
        return int(s)
    except ValueError:
        raise ValidationFailedException(f"{key}: not a number: {s}")


def extract_integers(key: Union[str, Sequence[str]]) -> Optional[List[IntRange]]:
    parts = extract_strings(key)
    if not parts:
        # nothing to do
        return None

    def _parse_range(part: str):
        if "-" not in part:
            return int(part)
        r = part.split("-", 2)
        first = int(r[0])
        last = int(r[1])
        if first == last:
            # the first and last numbers are the same, just treat it as a singe value
            return first
        elif last > first:
            # add the range as an array
            return (first, last)
        # the range is inverted, this is an error
        raise ValidationFailedException(f"{key}: the given range is inverted")

    try:
        values = [_parse_range(part) for part in parts]
        # check for invalid values
        return None if any(v is None for v in values) else values
    except ValueError as e:
        raise ValidationFailedException(f"{key}: not a number: {str(e)}")


def parse_date(s: str) -> int:
    # parses a given string in format YYYYMMDD or YYYY-MM-DD to a number in the form YYYYMMDD
    try:
        if s == "*":
            return s
        else:
            if len(s) > 10:  # max len of date is 10 (YYYY-MM-DD format)
                raise ValueError
            return int(s.replace("-", ""))
    except ValueError:
        raise ValidationFailedException(f"not a valid date: {s}")


def extract_date(key: Union[str, Sequence[str]]) -> Optional[int]:
    s = _extract_value(key)
    if not s:
        return None
    return parse_date(s)


def extract_dates(key: Union[str, Sequence[str]]) -> Optional[TimeValues]:
    parts = extract_strings(key)
    if not parts:
        return None
    values: TimeValues = []

    for part in parts:
        if part == "*":
            return ["*"]
        if ":" in part:
            # YYYY-MM-DD:YYYY-MM-DD
            range_part = part.split(":", 1)
            r = _verify_range(parse_date(range_part[0]), parse_date(range_part[1]))
            if r is None:
                return None
            values.append(r)
            continue
        # parse other date formats
        dashless_part = part.replace("-", "")
        if len(dashless_part) in (6, 12):
            # if there are 6 or 12 (hopefully) integers in this, it
            # should be a week or week range (YYYYWW or YYYYWWYYYYWW)
            r = parse_week_value(part)
        else:
            # else its (presumably) 8 or 16, which should mean day or
            # day range (YYYYMMDD or YYYYMMDDYYYYMMDD)...
            # other time types tbd lol
            r = parse_day_value(part)
        values.append(r)
    return values

def parse_source_signal_sets() -> List[SourceSignalSet]:
    ds = request.values.get("data_source")
    if ds:
        # old version
        require_any(request, "signal", "signals", empty=True)
        signals = extract_strings(("signals", "signal"))
        if len(signals) == 1 and signals[0] == "*":
            return [SourceSignalSet(ds, True)]
        return [SourceSignalSet(ds, signals)]

    if ":" not in request.values.get("signal", ""):
        raise ValidationFailedException("missing parameter: signal or (data_source and signal[s])")

    return parse_source_signal_arg()


def parse_geo_sets() -> List[GeoSet]:
    geo_type = request.values.get("geo_type")

    if geo_type:
        # old version
        require_any(request, "geo_value", "geo_values", empty=True)
        geo_values = extract_strings(("geo_values", "geo_value"))
        if len(geo_values) == 1 and geo_values[0] == "*":
            return [GeoSet(geo_type, True)]
        return [GeoSet(geo_type, geo_values)]

    if ":" not in request.values.get("geo", ""):
        raise ValidationFailedException("missing parameter: geo or (geo_type and geo_value[s])")

    return parse_geo_arg()


def parse_time_set() -> TimeSet:
    time_type = request.values.get("time_type")
    if time_type:
        # old version
        require_all(request, "time_type", "time_values")
        time_values = extract_dates("time_values")
        if time_values == ["*"]:
            return TimeSet(time_type, True)
        return TimeSet(time_type, time_values)

    if ":" not in request.values.get("time", ""):
        raise ValidationFailedException("missing parameter: time or (time_type and time_values)")

    return parse_time_arg()
