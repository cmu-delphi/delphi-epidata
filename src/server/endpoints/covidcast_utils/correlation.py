from dataclasses import dataclass, asdict
from typing import Optional, Iterable, Tuple
from scipy.stats import linregress
import pandas as pd


@dataclass
class CorrelationResult:
    geo_type: str
    geo_value: str
    signal_source: str
    signal_signal: str

    lag: int
    r2: float

    slope: float
    """
    y = slope * x + intercept
    """
    intercept: float
    """
    y = slope * x + intercept
    """
    samples: int
    """
    number of dates used for the regression line
    """

    def asdict(self):
        return asdict(self)


def compute_correlations(geo_type: str, geo_value: str, signal_source: str, signal_signal: str, lag: int, x: pd.DataFrame, y: pd.DataFrame) -> Iterable[CorrelationResult]:
    """
    x,y ... DataFrame with "time_value" as index and "value" column
    """
    xy = x.join(y, how="inner", lsuffix="_x", rsuffix="_y")
    for current_lag in range(-lag, lag + 1):
        print(current_lag)
        # TODO shift data by lag
        yield compute_correlation(geo_type, geo_value, signal_source, signal_signal, current_lag, xy)


def compute_correlation(geo_type: str, geo_value: str, signal_source: str, signal_signal: str, lag: int, xy: pd.DataFrame) -> CorrelationResult:
    model = linregress(xy.to_numpy())
    return CorrelationResult(geo_type, geo_value, signal_source, signal_signal, lag, r2=float(model.rvalue), intercept=float(model.intercept), slope=float(model.slope), samples=len(xy))
