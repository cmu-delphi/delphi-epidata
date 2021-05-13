from dataclasses import dataclass, asdict
from typing import Optional, Iterable, Tuple, Dict, List, Callable
from enum import Enum
from collections import OrderedDict
from ...utils import shift_time_value


class TrendEnum(str, Enum):
    unknown = "unknown"
    increasing = "increasing"
    decreasing = "decreasing"
    steady = "steady"


@dataclass
class Trend:
    geo_type: str
    geo_value: str
    signal_source: str
    signal_signal: str

    date: int
    value: Optional[float] = None

    basis_date: Optional[int] = None
    basis_value: Optional[float] = None
    basis_trend: TrendEnum = TrendEnum.unknown

    min_date: Optional[int] = None
    min_value: Optional[float] = None
    min_trend: TrendEnum = TrendEnum.unknown

    max_date: Optional[int] = None
    max_value: Optional[float] = None
    max_trend: TrendEnum = TrendEnum.unknown

    def asdict(self):
        return asdict(self)


def compute_trend(geo_type: str, geo_value: str, signal_source: str, signal_signal: str, current_time: int, basis_time: int, rows: Iterable[Tuple[int, float]]) -> Trend:
    t = Trend(geo_type, geo_value, signal_source, signal_signal, date=current_time, basis_date=basis_time)

    # find all needed rows
    for time, value in rows:
        if time == current_time:
            t.value = value
        if time == basis_time:
            t.basis_value = value
        if t.min_value is None or t.min_value > value:
            t.min_date = time
            t.min_value = value
        if t.max_value is None or t.max_value < value:
            t.max_date = time
            t.max_value = value

    if t.value is None or t.min_value is None:
        # cannot compute trend if current time is not found
        return t

    t.basis_trend = compute_trend_class(compute_trend_value(t.value, t.basis_value, t.min_value)) if t.basis_value else TrendEnum.unknown
    t.min_trend = compute_trend_class(compute_trend_value(t.value, t.min_value, t.min_value))
    t.max_trend = compute_trend_class(compute_trend_value(t.value, t.max_value, t.min_value)) if t.max_value else TrendEnum.unknown

    return t


def compute_trends(geo_type: str, geo_value: str, signal_source: str, signal_signal: str, shifter: Callable[[int], int], rows: Iterable[Tuple[int, float]]) -> List[Trend]:
    min_value: Optional[float] = None
    min_date: Optional[int] = None
    max_value: Optional[float] = None
    max_date: Optional[int] = None

    lookup: Dict[int, float] = OrderedDict()
    # find all needed rows
    for time, value in rows:
        lookup[time] = value
        if min_value is None or min_value > value:
            min_date = time
            min_value = value
        if max_value is None or max_value < value:
            max_date = time
            max_value = value

    trends: List[Trend] = []
    for current_time, value in lookup.items():
        basis_time = shifter(current_time)
        basis_value = lookup.get(basis_time, None)
        t = Trend(
            geo_type,
            geo_value,
            signal_source,
            signal_signal,
            date=current_time,
            value=value,
            basis_date=basis_time if basis_value is not None else None,
            basis_value=basis_value,
            min_date=min_date,
            min_value=min_value,
            max_date=max_date,
            max_value=max_value,
        )

        trends.append(t)

        if t.value is None or t.min_value is None:
            continue

        t.basis_trend = compute_trend_class(compute_trend_value(t.value, t.basis_value, t.min_value)) if t.basis_value else TrendEnum.unknown
        t.min_trend = compute_trend_class(compute_trend_value(t.value, t.min_value, t.min_value))
        t.max_trend = compute_trend_class(compute_trend_value(t.value, t.max_value, t.min_value)) if t.max_value else TrendEnum.unknown

    return trends


def compute_trend_value(current: float, basis: float, min_value: float) -> float:
    # based on www-covidcast
    normalized_basis = basis - min_value
    normalized_current = current - min_value
    if normalized_basis == normalized_current:
        return 0
    if normalized_basis == 0:
        return 1
    return normalized_current / normalized_basis - 1


def compute_trend_class(trend_value: float) -> TrendEnum:
    if trend_value >= 0.1:
        return TrendEnum.increasing
    if trend_value <= -0.1:
        return TrendEnum.decreasing
    return TrendEnum.steady
