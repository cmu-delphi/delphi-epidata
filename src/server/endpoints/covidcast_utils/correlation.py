from dataclasses import dataclass, asdict
from typing import Iterable
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


@dataclass
class Correlation:
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


def lag_join(lag: int, x: pd.DataFrame, y: pd.DataFrame, is_day = True) -> pd.DataFrame:
    # x_t_i ~ y_t_(i-lag)
    # aka x_t_(i+lag) ~ y_t_i

    if lag == 0:
        x_shifted = x
        y_shifted = y
    elif lag > 0:
        # x_t_i ~ y_shifted_t_i
        # shift y such that y_t(i - lag) -> y_shifted_t_i
        x_shifted = x
        y_shifted = y.shift(lag, freq="D" if is_day else 'W')
    else:  # lag < 0
        # x_shifted_t_i ~ y_t_i
        # shift x such that x_t(i+lag) -> x_shifted_t_i
        # lag < 0 -> - - lag = + lag
        x_shifted = x.shift(-lag, freq="D" if is_day else 'W')
        y_shifted = y
    # inner join to remove invalid pairs
    r = x_shifted.join(y_shifted, how="inner", lsuffix="_x", rsuffix="_y")
    return r.rename(columns=dict(value_x="x", value_y="y"))


def compute_correlations(geo_type: str, geo_value: str, signal_source: str, signal_signal: str, lag: int, x: pd.DataFrame, y: pd.DataFrame, is_day = True) -> Iterable[CorrelationResult]:
    """
    x,y ... DataFrame with "time_value" (Date) index and "value" (float) column
    """
    for current_lag in range(-lag, lag + 1):
        xy = lag_join(current_lag, x, y, is_day)
        c = compute_correlation(xy)

        yield CorrelationResult(geo_type, geo_value, signal_source, signal_signal, current_lag, r2=c.r2, intercept=c.intercept, slope=c.slope, samples=c.samples)


def compute_correlation(xy: pd.DataFrame) -> Correlation:
    if len(xy) < 2:
        # won't be a useful one
        return Correlation(0, 0, 0, len(xy))

    model = linregress(xy.to_numpy())
    r2 = float(model.rvalue) ** 2
    return Correlation(r2, float(model.slope), float(model.intercept), len(xy))
