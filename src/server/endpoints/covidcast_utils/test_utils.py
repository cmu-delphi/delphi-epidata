from numbers import Number
from typing import Iterable, List, Optional
from delphi.epidata.server.endpoints.covidcast_utils.model import DataSource, DataSignal
from more_itertools import windowed


# fmt: off
DATA_SIGNALS_BY_KEY = {
    ("src", "sig_diff"): DataSignal(
        source="src",
        signal="sig_diff",
        signal_basename="sig_base",
        name="src",
        active=True,
        short_description="",
        description="",
        time_label="",
        value_label="",
        is_cumulative=False,
        compute_from_base=True,
    ),
    ("src", "sig_smooth"): DataSignal(
        source="src",
        signal="sig_smooth",
        signal_basename="sig_base",
        name="src",
        active=True,
        short_description="",
        description="",
        time_label="",
        value_label="",
        is_cumulative=True,
        is_smoothed=True,
        compute_from_base=True,
    ),
    ("src", "sig_diff_smooth"): DataSignal(
        source="src",
        signal="sig_diff_smooth",
        signal_basename="sig_base",
        name="src",
        active=True,
        short_description="",
        description="",
        time_label="",
        value_label="",
        is_cumulative=False,
        is_smoothed=True,
        compute_from_base=True,
    ),
    ("src", "sig_base"): DataSignal(
        source="src",
        signal="sig_base",
        signal_basename="sig_base",
        name="src",
        active=True,
        short_description="",
        description="",
        time_label="",
        value_label="",
        is_cumulative=True,
    ),
    ("src2", "sig_base"): DataSignal(
        source="src2",
        signal="sig_base",
        signal_basename="sig_base",
        name="sig_base",
        active=True,
        short_description="",
        description="",
        time_label="",
        value_label="",
        is_cumulative=True,
    ),
    ("src2", "sig_diff_smooth"): DataSignal(
        source="src2",
        signal="sig_diff_smooth",
        signal_basename="sig_base",
        name="sig_smooth",
        active=True,
        short_description="",
        description="",
        time_label="",
        value_label="",
        is_cumulative=False,
        is_smoothed=True,
        compute_from_base=True,
    ),
}

DATA_SOURCES_BY_ID = {
    "src": DataSource(
        source="src",
        db_source="src",
        name="src",
        description="",
        reference_signal="sig_base",
        signals=[DATA_SIGNALS_BY_KEY[key] for key in DATA_SIGNALS_BY_KEY if key[0] == "src"],
    ),
    "src2": DataSource(
        source="src2",
        db_source="src2",
        name="src2",
        description="",
        reference_signal="sig_base",
        signals=[DATA_SIGNALS_BY_KEY[key] for key in DATA_SIGNALS_BY_KEY if key[0] == "src2"],
    ),
}
# fmt: on


def _diff_rows(rows: Iterable[Number]) -> List[Number]:
    return [round(float(y - x), 8) if not (x is None or y is None) else None for x, y in windowed(rows, 2)]


def _smooth_rows(rows: Iterable[Number], window_length: int = 7, kernel: Optional[List[Number]] = None):
    if not kernel:
        kernel = [1.0 / window_length] * window_length
    return [round(sum(x * y for x, y in zip(window, kernel)), 8) if None not in window else None for window in windowed(rows, len(kernel))]


def _reindex_windowed(lst: list, window_length: int) -> list:
    return [max(window) if None not in window else None for window in windowed(lst, window_length)]

