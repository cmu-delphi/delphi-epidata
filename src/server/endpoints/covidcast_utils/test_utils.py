import numpy as np
import pandas as pd

from delphi_utils.nancodes import Nans
from delphi.epidata.acquisition.covidcast.covidcast_row import CovidcastRows, set_df_dtypes
from delphi.epidata.server.endpoints.covidcast_utils.model import DataSource, DataSignal
from delphi.epidata.server.utils.dates import iterate_over_range


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


# A slow JIT method to sanity check values.
def reindex_df(df: pd.DataFrame) -> pd.DataFrame:
    dfs = []
    for key, group_df in df.groupby(["source", "signal", "geo_value"]):
        group_df = group_df.set_index("time_value").sort_index()
        group_df = group_df.reindex(iterate_over_range(group_df.index.min(), group_df.index.max(), inclusive=True))
        group_df["source"] = group_df["source"].ffill()
        group_df["signal"] = group_df["signal"].ffill()
        group_df["geo_value"] = group_df["geo_value"].ffill()
        group_df["geo_type"] = group_df["geo_type"].ffill()
        group_df["time_type"] = group_df["time_type"].ffill()
        group_df["missing_value"] = np.where(group_df["value"].isna(), Nans.NOT_APPLICABLE, Nans.NOT_MISSING)
        group_df["missing_stderr"] = np.where(group_df["stderr"].isna(), Nans.NOT_APPLICABLE, Nans.NOT_MISSING)
        group_df["missing_sample_size"] = np.where(group_df["sample_size"].isna(), Nans.NOT_APPLICABLE, Nans.NOT_MISSING)
        dfs.append(group_df.reset_index())
    ndf = pd.concat(dfs)
    ndf = set_df_dtypes(ndf, CovidcastRows._pandas_dtypes)
    return ndf

def diff_df(df: pd.DataFrame, signal_name: str, nan_fill_value: float = np.nan, omit_left_boundary: bool = False) -> pd.DataFrame:
    df = df.copy()
    dfs = []
    for key, group_df in df.groupby(["source", "signal", "geo_value"]):
        group_df = group_df.set_index("time_value").sort_index()
        group_df["value"] = group_df["value"].fillna(nan_fill_value).diff()
        group_df["stderr"] = np.nan
        group_df["sample_size"] = np.nan
        group_df["missing_value"] = np.where(group_df["value"].isna(), Nans.NOT_APPLICABLE, Nans.NOT_MISSING)
        group_df["missing_stderr"] = Nans.NOT_APPLICABLE
        group_df["missing_sample_size"] = Nans.NOT_APPLICABLE
        group_df["issue"] = group_df["issue"].rolling(2).max()
        group_df["lag"] = group_df["lag"].rolling(2).max()
        group_df["signal"] = signal_name
        if omit_left_boundary:
            group_df = group_df.iloc[1:]
        dfs.append(group_df.reset_index())
    ndf = pd.concat(dfs)
    ndf = set_df_dtypes(ndf, CovidcastRows._pandas_dtypes)
    return ndf

def smooth_df(df: pd.DataFrame, signal_name: str, nan_fill_value: float = np.nan, window_length: int = 7, omit_left_boundary: bool = False) -> pd.DataFrame:
    df = df.copy()
    df["time_value"] = pd.to_datetime(df["time_value"], format="%Y%m%d")
    dfs = []

    for key, group_df in df.groupby(["source", "signal", "geo_value"]):
        group_df = group_df.set_index("time_value").sort_index()
        group_df["value"] = group_df["value"].fillna(nan_fill_value).rolling(f"{window_length}D", min_periods=window_length-1).mean()
        group_df["stderr"] = np.nan
        group_df["sample_size"] = np.nan
        group_df["missing_value"] = np.where(group_df["value"].isna(), Nans.NOT_APPLICABLE, Nans.NOT_MISSING)
        group_df["missing_stderr"] = Nans.NOT_APPLICABLE
        group_df["missing_sample_size"] = Nans.NOT_APPLICABLE
        group_df["issue"] = group_df["issue"].rolling(7).max()
        group_df["lag"] = group_df["lag"].rolling(7).max()
        group_df["signal"] = signal_name
        if omit_left_boundary:
            group_df = group_df.iloc[window_length - 1:]
        dfs.append(group_df.reset_index())
    ndf = pd.concat(dfs)
    ndf["time_value"] = ndf["time_value"].dt.strftime("%Y%m%d")
    ndf = set_df_dtypes(ndf, CovidcastRows._pandas_dtypes)
    return ndf

def diff_smooth_df(df: pd.DataFrame, signal_name: str, nan_fill_value: float = np.nan, window_length: int = 7, omit_left_boundary: bool = False) -> pd.DataFrame:
    return smooth_df(diff_df(df, signal_name, nan_fill_value=nan_fill_value, omit_left_boundary=omit_left_boundary), signal_name, nan_fill_value=nan_fill_value, window_length=window_length, omit_left_boundary=omit_left_boundary)
