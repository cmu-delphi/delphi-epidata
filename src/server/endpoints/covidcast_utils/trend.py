from dataclasses import dataclass, asdict
from typing import Optional, Iterable, Tuple
from datetime import date
from enum import Enum


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

    value: Optional[float] = None

    basis_date: Optional[date] = None
    basis_value: Optional[float] = None
    basis_trend: TrendEnum = TrendEnum.unknown

    min_date: Optional[date] = None
    min_value: Optional[float] = None
    min_trend: TrendEnum = TrendEnum.unknown

    max_date: Optional[date] = None
    max_value: Optional[float] = None
    max_trend: TrendEnum = TrendEnum.unknown

    def asdict(self):
        return asdict(self)


def compute_trend(geo_type: str, geo_value: str, signal_source: str, signal_signal: str, time_value: int, rows: Iterable[Tuple[int, float]]) -> Trend:
    t = Trend(geo_type, geo_value, signal_source, signal_signal)
    # TODO
    return t
