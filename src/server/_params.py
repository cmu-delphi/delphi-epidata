import re
from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple, Union

from flask import request

from ._exceptions import ValidationFailedException


def _parse_common_multi_arg(key: str) -> List[Tuple[str, Union[bool, Sequence[str]]]]:
    line = ';'.join(request.values.getlist(key))

    parsed: List[Tuple[str, Union[bool, Sequence[str]]]] = []

    if not line:
        return parsed

    pattern = re.compile(r'^(\w+):(.*)$', re.MULTILINE)
    for entry in line.split(';'):
        m = pattern.match(entry)
        if not m:
            raise ValidationFailedException(f"{key} param: {entry} is not matching <{key}_type>:<{key}_values> syntax")
        group_type = m.group(1).strip()
        group_value = m.group(2).strip()
        if group_value == '*':
            parsed.append((group_type, True))
        else:
            parsed.append((group_type, [g.strip() for g in group_value.split(',')]))
    return parsed


@dataclass
class GeoPair:
    geo_type: str
    geo_values: Union[bool, Sequence[str]]


def parse_geo_arg() -> List[GeoPair]:
    return [GeoPair(geo_type, geo_values) for [geo_type, geo_values] in _parse_common_multi_arg('geo')]


@dataclass
class SourceSignalPair:
    source: str
    signal: Union[bool, Sequence[str]]


def parse_source_signal_arg() -> List[SourceSignalPair]:
    return [SourceSignalPair(source, signals) for [source, signals] in _parse_common_multi_arg('signals')]


@dataclass
class TimePair:
    time_type: str
    time_values: Union[bool, Sequence[Union[int, Tuple[int, int]]]]


def parse_week_values(time_values: Sequence[str]) -> Sequence[Union[int, Tuple[int, int]]]:
    # TODO
    return []


def parse_day_values(time_values: Sequence[str]) -> Sequence[Union[int, Tuple[int, int]]]:
    # TODO
    return []


def parse_time_arg() -> List[TimePair]:
    def parse(time_type: str, time_values: Union[bool, Sequence[str]]) -> TimePair:
        if isinstance(time_values, bool):
            return TimePair(time_type, time_values)

        if time_type == 'week':
            return TimePair('week', parse_week_values(time_values))
        return TimePair('day', parse_day_values(time_values))

    return [parse(time_type, time_values) for [time_type, time_values] in _parse_common_multi_arg('time')]
