from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import timedelta
from enum import Enum
from itertools import chain, groupby, tee
from numbers import Number
from typing import Any, Callable, Generator, Iterable, Iterator, Optional, Dict, List, Set, Tuple, Union

from pathlib import Path
import re
import pandas as pd
import numpy as np

from delphi_utils.nancodes import Nans
from ..._params import SourceSignalPair, TimePair
from ...utils import shift_day_value, day_to_time_value, time_value_to_day, iterate_over_range


PANDAS_DTYPES = {
    "source": str,
    "signal": str,
    "time_type": str,
    "time_value": int,
    "geo_type": str,
    "geo_value": str,
    "value": float,
    "stderr": float,
    "sample_size": float,
    "missing_value": "Int8",
    "missing_stderr": "Int8",
    "missing_sample_size": "Int8",
    "issue": "Int64",
    "lag": "Int64",
    "id": "Int64",
    "direction": "Int8",
    "direction_updated_timestamp": "Int64",
    "value_updated_timestamp": "Int64",
}
PANDAS_DTYPES_TIME = {
    "source": str,
    "signal": str,
    "time_type": str,
    "time_value": "datetime64[ns]",
    "geo_type": str,
    "geo_value": str,
    "value": float,
    "stderr": float,
    "sample_size": float,
    "missing_value": "Int8",
    "missing_stderr": "Int8",
    "missing_sample_size": "Int8",
    "issue": "Int64",
    "lag": "Int64",
    "id": "Int64",
    "direction": "Int8",
    "direction_updated_timestamp": "Int64",
    "value_updated_timestamp": "Int64",
}


class SeriesTransform(str, Enum):
    identity = "identity"
    diff = "diff"
    smooth = "smooth"
    diff_smooth = "diff_smooth"


@dataclass(frozen=True)
class SourceSignal:
    source: str
    signal: str


class HighValuesAre(str, Enum):
    bad = "bad"
    good = "good"
    neutral = "neutral"


class SignalFormat(str, Enum):
    per100k = "per100k"
    percent = "percent"
    fraction = "fraction"
    raw_count = "raw_count"
    raw = "raw"
    count = "count"


class SignalCategory(str, Enum):
    public = "public"
    early = "early"
    late = "late"
    cases_testing = "cases_testing"
    other = "other"


class TimeType(str, Enum):
    day = "day"
    week = "week"


@dataclass
class WebLink:
    alt: str
    href: str


def _fix_links(link: Optional[str]) -> List[WebLink]:
    # fix the link structure as given in (multiple) optional markdown link formats
    if not link:
        return []

    reg = re.compile(r"\[(.+)\]\s*\((.*)\)")

    def parse(l: str) -> Optional[WebLink]:
        l = l.strip()
        if not l:
            return None
        m = reg.match(l)
        if not m:
            return WebLink("API Documentation", l)
        return WebLink(m.group(1), m.group(2))

    return [l for l in map(parse, link.split(",")) if l]


@dataclass
class DataSignal:
    source: str
    signal: str
    signal_basename: str
    name: str
    active: bool
    short_description: str
    description: str
    time_label: str
    value_label: str
    format: SignalFormat = SignalFormat.raw
    category: SignalCategory = SignalCategory.other
    high_values_are: HighValuesAre = HighValuesAre.neutral
    is_smoothed: bool = False
    is_weighted: bool = False
    is_cumulative: bool = False
    has_stderr: bool = False
    has_sample_size: bool = False
    link: List[WebLink] = field(default_factory=list)
    compute_from_base: bool = False
    time_type: TimeType = TimeType.day

    def __post_init__(self):
        self.link = _fix_links(self.link)

    def initialize(self, source_map: Dict[str, "DataSource"], map: Dict[Tuple[str, str], "DataSignal"], initialized: Set[Tuple[str, str]]):
        # mark as initialized
        initialized.add(self.key)

        base = map.get((self.source, self.signal_basename))
        if base and base.key not in initialized:
            # initialize base first
            base.initialize(source_map, map, initialized)

        source = source_map.get(self.source)

        if not self.name:
            self.name = base.name if base else self.signal
        if not self.description:
            if base:
                self.description = base.description or base.short_description or "No description available"
            else:
                self.description = self.short_description or "No description available"
        if not self.short_description:
            if base:
                self.short_description = base.short_description or (base.description[:10] if base.description else "No description available")
            else:
                self.short_description = self.description[:10]
        if not self.link and base:
            self.link = base.link
        if not self.value_label:
            self.value_label = base.value_label if base else "Value"
        if not self.category:
            self.value_label = base.category if base else SignalCategory.other
        if not self.high_values_are:
            self.high_values_are = base.high_values_are if base else HighValuesAre.neutral

        self._replace_placeholders(base, source)

    def _replace_placeholders(self, base: Optional["DataSignal"], source: Optional["DataSource"]):
        text_replacements = {
            "base_description": base.description if base else "",
            "base_short_description": base.short_description if base else "",
            "base_name": base.name if base else "",
            "source_name": source.name if source else "",
            "source_description": source.description if source else "",
        }

        def replace_group(match: re.Match) -> str:
            key = match.group(1)
            if key and key in text_replacements:
                return text_replacements[key]
            return key

        def replace_replacements(text: str) -> str:
            return re.sub(r"\{([\w_]+)\}", replace_group, text)

        self.name = replace_replacements(self.name)
        # add new replacement on the fly for the next one
        text_replacements["name"] = self.name
        self.short_description = replace_replacements(self.short_description)
        text_replacements["short_description"] = self.short_description
        self.description = replace_replacements(self.description)

    def asdict(self):
        return asdict(self)

    @property
    def key(self) -> Tuple[str, str]:
        return (self.source, self.signal)


@dataclass
class DataSource:
    source: str
    db_source: str
    name: str
    description: str
    reference_signal: str
    license: Optional[str] = None
    link: List[WebLink] = field(default_factory=list)
    dua: Optional[str] = None

    signals: List[DataSignal] = field(default_factory=list)

    def __post_init__(self):
        self.link = _fix_links(self.link)
        if not self.db_source:
            self.db_source = self.source

    def asdict(self):
        r = asdict(self)
        r["signals"] = [r.asdict() for r in self.signals]
        return r

    @property
    def uses_db_alias(self):
        return self.source != self.db_source


def _clean_column(c: str) -> str:
    r = c.lower().replace(" ", "_").replace("-", "_").strip()
    if r == "source_subdivision":
        return "source"
    return r


_base_dir = Path(__file__).parent


def _load_data_sources():
    data_sources_df: pd.DataFrame = pd.read_csv(_base_dir / "db_sources.csv")
    data_sources_df = data_sources_df.replace({np.nan: None})
    data_sources_df.columns = map(_clean_column, data_sources_df.columns)
    data_sources: List[DataSource] = [DataSource(**d) for d in data_sources_df.to_dict(orient="records")]
    data_sources_df.set_index("source")
    return data_sources, data_sources_df


data_sources, data_sources_df = _load_data_sources()
data_sources_by_id = {d.source: d for d in data_sources}


def _load_data_signals(sources: List[DataSource]):
    by_id = {d.source: d for d in sources}
    data_signals_df: pd.DataFrame = pd.read_csv(_base_dir / "db_signals.csv")
    data_signals_df = data_signals_df.replace({np.nan: None})
    data_signals_df.columns = map(_clean_column, data_signals_df.columns)
    ignore_columns = {"base_is_other"}
    data_signals: List[DataSignal] = [DataSignal(**{k: v for k, v in d.items() if k not in ignore_columns}) for d in data_signals_df.to_dict(orient="records")]
    data_signals_df.set_index(["source", "signal"])

    by_source_id = {d.key: d for d in data_signals}
    initialized: Set[Tuple[str, str]] = set()
    for ds in data_signals:
        ds.initialize(by_id, by_source_id, initialized)

    for ds in data_signals:
        source = by_id.get(ds.source)
        if source:
            source.signals.append(ds)

    return data_signals, data_signals_df


data_signals, data_signals_df = _load_data_signals(data_sources)
data_signals_by_key = {d.key: d for d in data_signals}
# also add the resolved signal version to the signal lookup
for d in data_signals:
    source = data_sources_by_id.get(d.source)
    if source and source.uses_db_alias:
        data_signals_by_key[(source.db_source, d.signal)] = d


def get_related_signals(data_signal: DataSignal) -> List[DataSignal]:
    return [s for s in data_signals if s != data_signal and s.signal_basename == data_signal.signal_basename]


def count_signal_time_types(source_signals: List[SourceSignalPair]) -> Tuple[int, int]:
    """
    count the number of signals in this query for each time type
    @returns daily counts, weekly counts
    """
    weekly = 0
    daily = 0
    for pair in source_signals:
        if pair.signal == True:
            continue
        for s in pair.signal:
            signal = data_signals_by_key.get((pair.source, s))
            if not signal:
                continue
            if signal.time_type == TimeType.week:
                weekly += 1
            else:
                daily += 1
    return daily, weekly


def create_source_signal_alias_mapper(source_signals: List[SourceSignalPair]) -> Tuple[List[SourceSignalPair], Optional[Callable[[str, str], str]]]:
    """Create a mapper function that maps a source and signal to the actual source and signal in the database.
    
    Some sources have a different name in the API than in the database: 

        db name                 | api name
        ------------------------|----------------
        indicator-combination   | indicator-combination-cases-deaths
        quidel                  | quidel-covid-ag
        safegraph               | safegraph-weekly
        indicator-combination   | indicator-combination-nmf
        quidel                  | quidel-flu
        safegraph               | safegraph-daily

    (Double check the db_sources.csv file as this comment may be out of date; first column is the db name, second column is the api name.
    That file is sourced from a Google Sheet in tasks.py at the root of this repo.)

    This function creates a mapper function that maps the source and signal from the database name back to the API name when returning the request.
    """
    alias_to_data_sources: Dict[str, List[DataSource]] = {}
    transformed_pairs: List[SourceSignalPair] = []
    for pair in source_signals:
        source = data_sources_by_id.get(pair.source)
        if not source or not source.uses_db_alias:
            transformed_pairs.append(pair)
            continue
        # uses an alias
        alias_to_data_sources.setdefault(source.db_source, []).append(source)
        if pair.signal is True:
            # list all signals of this source (*) so resolve to a plain list of all in this alias
            transformed_pairs.append(SourceSignalPair(source.db_source, [s.signal for s in source.signals]))
        else:
            transformed_pairs.append(SourceSignalPair(source.db_source, pair.signal))

    if not alias_to_data_sources:
        # no alias needed
        return source_signals, None

    def map_row(source: str, signal: str) -> str:
        """
        maps a given row source back to its alias version
        """
        possible_data_sources = alias_to_data_sources.get(source)
        if not possible_data_sources:
            # nothing to transform
            return source
        if len(possible_data_sources) == 1:
            return possible_data_sources[0].source
        # need the signal to decide
        signal_source = next((f for f in possible_data_sources if any((s.signal == signal for s in f.signals))), None)
        if not signal_source:
            # take the first one
            signal_source = possible_data_sources[0]
        return signal_source.source

    return transformed_pairs, map_row


def reindex_iterable(iterator: Iterator[Dict], fill_value: Optional[Number] = None) -> Iterator[Dict]:
    """Produces an iterator that fills in gaps in the time values of another iterator.
    Used to produce an iterator with a contiguous time index for time series operations.
    The iterator is assumed to be sorted by time_value in ascending order.
    The min and max time_values are determined from the first and last rows of the iterator.
    The fill_value is used to fill in gaps in the time index.
    """
    # Since we're looking ahead, we need to keep a buffer of the last item.
    peek_memory = []

    # If the iterator is empty, we halt immediately.
    iterator = iter(iterator)
    try:
        first_item = next(iterator)
        peek_memory.append(first_item)
    except StopIteration:
        return

    _default_item = first_item.copy()
    _default_item.update({
        "stderr": None,
        "sample_size": None,
        "issue": None,
        "lag": None,
        "missing_stderr": Nans.NOT_APPLICABLE,
        "missing_sample_size": Nans.NOT_APPLICABLE,
        "id": None,
        "direction": None,
        "direction_updated_timestamp": None,
        "value_updated_timestamp": None
    })

    expected_time_value = first_item["time_value"]
    # Non-trivial operations otherwise.
    while True:
        try:
            if peek_memory:
                new_item = peek_memory.pop()
            else:
                new_item = next(iterator)
        except StopIteration:
            return

        if expected_time_value == new_item.get("time_value"):
            # Return the row we just peeked.
            yield new_item 
        else:
            # We've found a gap in the time index.
            # Put the new item back in the buffer.
            peek_memory.append(new_item)

            # Return a default row instead.
            # Copy to avoid Python by-reference memory issues.
            default_item = _default_item.copy()
            default_item.update(
                {
                    "time_value": expected_time_value,
                    "value": fill_value,
                    "missing_value": Nans.NOT_MISSING if pd.notna(fill_value) else Nans.NOT_APPLICABLE,
                }
            )
            yield default_item
        expected_time_value = day_to_time_value(time_value_to_day(expected_time_value) + timedelta(days=1))


def _reindex_iterable2(iterator: Iterator[dict], fill_value: Optional[Number] = None) -> Iterator[dict]:
    """Produces an iterator that fills in gaps in the time values of another iterator.

    Used to produce an iterator with a contiguous time index for time series operations.
    The iterator is assumed to be sorted by time_value in ascending order.
    The min and max time_values are determined from the first and last rows of the iterator.
    The fill_value is used to fill in gaps in the time index.
    """
    from more_itertools import peekable
    _iterator = peekable(iterator)

    # If the iterator is empty, we halt immediately.
    try:
        first_item = _iterator.peek()
    except StopIteration:
        return

    expected_time_value = first_item["time_value"]
    # Non-trivial operations otherwise.
    while True:
        try:
            # This will stay the same until the peeked element is consumed.
            new_item = _iterator.peek()
        except StopIteration:
            return

        if expected_time_value == new_item.get("time_value"):
            # Get the value we just peeked.
            t_ = next(_iterator)
            yield {
                "time_value": t_["time_value"],
                "value": t_["value"],
                "geo_value": t_["geo_value"],
                "source": t_["source"],
                "signal": t_["signal"],
                "geo_type": t_["geo_type"],
            }
        else:
            # Return a default row instead.
            yield {
                "time_value": expected_time_value,
                "value": fill_value,
                "geo_value": first_item["geo_value"],
                "source": first_item["source"],
                "signal": first_item["signal"],
                "geo_type": first_item["geo_type"],
            }
        expected_time_value = day_to_time_value(time_value_to_day(expected_time_value) + timedelta(days=1))


def get_base_signal_transform(signal: Union[DataSignal, Tuple[str, str]]) -> SeriesTransform:
    """Given a DataSignal, return the transformation that needs to be applied to its base signal to derive the signal."""
    if isinstance(signal, DataSignal):
        base_signal = data_signals_by_key.get((signal.source, signal.signal_basename))
        if signal.format not in [SignalFormat.raw, SignalFormat.raw_count, SignalFormat.count] or not signal.compute_from_base or not base_signal:
            return SeriesTransform.identity
        if signal.is_cumulative and signal.is_smoothed:
            return SeriesTransform.smooth
        if not signal.is_cumulative and not signal.is_smoothed:
            return SeriesTransform.diff if base_signal.is_cumulative else SeriesTransform.identity
        if not signal.is_cumulative and signal.is_smoothed:
            return SeriesTransform.diff_smooth if base_signal.is_cumulative else SeriesTransform.smooth
        return SeriesTransform.identity

    if isinstance(signal, tuple):
        if signal := data_signals_by_key.get(signal):
            return get_base_signal_transform(signal)
        return SeriesTransform.identity

    raise TypeError("signal must be either Tuple[str, str] or DataSignal.")


def get_transform_types(source_signal_pairs: List[SourceSignalPair]) -> Set[SeriesTransform]:
    """Return a collection of the unique transforms required for transforming a given source-signal pair list.

    Example:
    SourceSignalPair("src", ["sig", "sig_smoothed", "sig_diff"]) would return {IDENTITY, SMOOTH, DIFF}.

    Used to pad the user DB query with extra days.
    """
    transform_types = set()
    for source_signal_pair in source_signal_pairs:
        source_name = source_signal_pair.source
        signal_names = source_signal_pair.signal

        if isinstance(signal_names, bool):
            continue

        transform_types |= {get_base_signal_transform((source_name, signal_name)) for signal_name in signal_names}

    return transform_types


def get_pad_length(source_signal_pairs: List[SourceSignalPair], smoother_window_length: int):
    """Returns the size of the extra date padding needed, depending on the transformations the source-signal pair list requires.

    If smoothing is required, we fetch an extra smoother_window_length - 1 days (6 by default). If both diffing and smoothing is required on the same signal,
    then we fetch extra smoother_window_length days (7 by default).

    Used to pad the user DB query with extra days.
    """
    transform_types = get_transform_types(source_signal_pairs)
    pad_length = [0]
    if SeriesTransform.diff_smooth in transform_types:
        pad_length.append(smoother_window_length)
    if SeriesTransform.smooth in transform_types:
        pad_length.append(smoother_window_length - 1)
    if SeriesTransform.diff in transform_types:
        pad_length.append(1)
    return max(pad_length)


def pad_time_pair(time_pair: TimePair, pad_length: int) -> TimePair:
    """Pads a list of TimePairs with another TimePair that extends the smallest time value by the pad_length, if needed.

    Assumes day time_type, since this function is only called for JIT computations which share the same assumption.

    Example:
    [TimePair("day", [20210407])] with pad_length 6 would return [TimePair("day", [20210407]), TimePair("day", [(20210401, 20210407)])].
    """
    if pad_length < 0:
        raise ValueError("pad_length should be a positive integer.")

    if pad_length == 0:
        return time_pair

    if time_pair.time_type != "day":
        raise ValueError("pad_time_pair assumes day time_type.")

    min_time = float("inf")
    if not isinstance(time_pair.time_values, bool):
        for time_value in time_pair.time_values:
            min_time = min(min_time, time_value if isinstance(time_value, int) else time_value[0])

        padded_time = (shift_day_value(min_time, -1 * pad_length), min_time)
        time_pair = TimePair(time_pair.time_type, time_pair.time_values + [padded_time])

    return time_pair


def pad_time_window(time_window: TimePair, pad_length: int) -> TimePair:
    """Extend a TimePair with a single range time value on the left by pad_length.

    Example:
    (20210407, 20210413) with pad_length 6 would return (20210401, 20210413).

    Used to pad the user DB query with extra days.
    """
    if pad_length < 0:
        raise ValueError("pad_length should non-negative.")
    if pad_length == 0:
        return time_window
    if time_window.time_type != "day":
        raise ValueError("pad_time_window assumes day time_type.")
    if isinstance(time_window.time_values, bool):
        return time_window
    if len(time_window.time_values) != 1:
        raise ValueError("pad_time_window assumes a single time value.")
    min_time, max_time = time_window.time_values[0]
    return TimePair("day", [(shift_day_value(min_time, -1 * pad_length), max_time)])


def to_dict_custom(df: pd.DataFrame) -> Iterable[Dict[str, Any]]:
    """This is a workaround a performance bug in Pandas.

    - See this issue: https://github.com/pandas-dev/pandas/issues/46470,
    - The first if branch is to avoid using reset_index(), which I found to be a good deal slower than just reading the index,
    - All the dtype conversions are to avoid JSON serialization errors (e.g. numpy.int64).
    """
    df = df.reset_index()
    col_arr_map = {col: df[col].to_numpy(dtype=object, na_value=None) for col in df.columns}

    for i in range(len(df)):
        yield {col: col_arr_map[col][i] for col in df.columns}


def _set_df_dtypes(df: pd.DataFrame, dtypes: Dict[str, Any]) -> pd.DataFrame:
    """Set the dataframe column datatypes."""
    for d in dtypes.values():
        try:
            pd.api.types.pandas_dtype(d)
        except TypeError:
            raise ValueError(f"Invalid dtype {d}")

    sub_dtypes = {k: v for k, v in dtypes.items() if k in df.columns}
    return df.astype(sub_dtypes)


def generate_transformed_rows(
    rows: Iterable[Dict],
    transform_dict: Optional[Dict[SourceSignal, List[SourceSignal]]] = None,
    transform_args: Optional[Dict] = None,
    alias_mapper: Callable = None,
) -> pd.DataFrame:
    """Applies time-series transformations to streamed rows from a database.

    This function is written for performance, so many components are very fragile. Be careful.
    The codepaths for identity transform is so different because it needs to preserve the data in more columns than JIT methods,
    such as sample_size and stderr. Data loading is one of two key bottlenecks here (data unloading being the other), so we focus on it here.

    Parameters:
    rows: Iterator[Dict]
        An iterator streaming rows from a database query. Assumed to be sorted by source, signal, geo_type, geo_value, time_type, and time_value.
    transform_dict: Dict[SourceSignal, List[SourceSignal]], default None
        A dictionary mapping a base source-signal to a list of their derived source-signals that the user wishes to query.
        For example, transform_dict may be 
            {SourceSignal("jhu-csse", "confirmed_cumulative_num): [SourceSignal("jhu-csse", "confirmed_incidence_num"), SourceSignal("jhu-csse", "confirmed_7dav_incidence_num")]}.
    transform_args: Optional[Dict], default None
        A dictionary of keyword arguments for the transformer functions.
    alias_mapper: Callable, default None
        A function that maps a source-signal to an alias. This is used to bridge the source naming gap between the database and the API.

    Yields:
    transformed rows: Dict
        The transformed rows returned in an interleaved fashion. Non-transformed rows have the IDENTITY operation applied.
    """
    if not transform_args:
        transform_args = dict()
    if not transform_dict:
        transform_dict = dict()
    if not alias_mapper:
        alias_mapper = lambda source, signal: source

    dfs = []
    for (base_source_name, base_signal_name, geo_type), grouped_rows in groupby(rows, lambda x: (x["source"], x["signal"], x["geo_type"])):
        derived_signals = transform_dict.get(SourceSignal(base_source_name, base_signal_name), [])
        grouped_rows_tee = tee(grouped_rows, len(derived_signals))
        for (derived_signal, grouped_rows_copy) in zip(derived_signals, grouped_rows_tee):
            derived_signal_name = derived_signal.signal
            transform_type = get_base_signal_transform((base_source_name, derived_signal_name))

            if transform_type == SeriesTransform.identity:
                identity_row_cols = ["time_value", "geo_value", "value", "sample_size", "stderr", "missing_value", "missing_sample_size", "missing_stderr", "issue", "lag"]
                derived_df = pd.DataFrame(grouped_rows_copy, columns=identity_row_cols)
                derived_df["time_value"] = pd.to_datetime(derived_df["time_value"], format="%Y%m%d")

                # Set dtypes. Int8/Int64 are needed to allow null values.
                # TODO: Try using StringDType instead of object. Or categorical. This is mostly for memory usage. No worries about to_dict.
                derived_df = _set_df_dtypes(derived_df, PANDAS_DTYPES_TIME)

                derived_df = derived_df.set_index("time_value")

                derived_df = derived_df.assign(
                    source=alias_mapper(base_source_name, derived_signal_name),
                    signal=derived_signal_name,
                    geo_type=geo_type,
                    time_type="day",
                    direction=None
                )
                dfs.append(derived_df)
                continue

            derived_df = pd.DataFrame(grouped_rows_copy, columns=["time_value", "geo_value", "value", "issue", "lag"])
            derived_df["time_value"] = pd.to_datetime(derived_df["time_value"], format="%Y%m%d")

            # Set dtypes. Int8/Int64 are needed to allow null values.
            # TODO: Try using StringDType instead of object. Or categorical. This is mostly for memory usage. No worries about to_dict.
            derived_df = _set_df_dtypes(derived_df, PANDAS_DTYPES_TIME)

            derived_df = derived_df.set_index("time_value")

            if transform_type == SeriesTransform.diff:
                derived_df["value"] = derived_df.groupby("geo_value", sort=False)["value"].diff()
                window_length = 2
            elif transform_type == SeriesTransform.smooth:
                window_length = transform_args.get("smoother_window_length", 7)
                derived_df["value"] = derived_df.groupby("geo_value", sort=False)["value"].rolling(f"{window_length}D", min_periods=window_length-1).mean().droplevel(level=0)
            elif transform_type == SeriesTransform.diff_smooth:
                window_length = transform_args.get("smoother_window_length", 7)
                derived_df["value"] = derived_df.groupby("geo_value", sort=False)["value"].diff()
                derived_df["value"] = derived_df.groupby("geo_value", sort=False)["value"].rolling(f"{window_length}D", min_periods=window_length-1).mean().droplevel(level=0)
                window_length += 1
            else:
                raise ValueError(f"Unknown transform for {derived_signal}.")

            derived_df = derived_df.assign(
                source=alias_mapper(base_source_name, derived_signal_name),
                signal=derived_signal_name,
                issue=derived_df.groupby("geo_value", sort=False)["issue"].rolling(window_length).max().droplevel(level=0).astype("Int64") if "issue" in derived_df.columns else None,
                lag=derived_df.groupby("geo_value", sort=False)["lag"].rolling(window_length).max().droplevel(level=0).astype("Int64") if "lag" in derived_df.columns else None,
                stderr=np.nan,
                sample_size=np.nan,
                missing_value=np.where(derived_df["value"].isna(), Nans.NOT_APPLICABLE, Nans.NOT_MISSING),
                missing_stderr=Nans.NOT_APPLICABLE,
                missing_sample_size=Nans.NOT_APPLICABLE,
                time_type="day",
                geo_type=geo_type,
                direction=None,
            )
            dfs.append(derived_df)

    if not dfs:
        return pd.DataFrame()

    derived_df_full = pd.concat(dfs)
    # Ok to do in place because there are no other references to this memory chunk.
    derived_df_full.reset_index(inplace=True)
    derived_df_full["time_value"] = derived_df_full["time_value"].dt.strftime("%Y%m%d").astype("Int64")
    return derived_df_full


def get_basename_signals_and_derived_map(source_signal_pairs: List[SourceSignalPair]) -> Tuple[List[SourceSignalPair], Dict[SourceSignal, List[SourceSignal]]]:
    """From a list of SourceSignalPairs, return the base signals required to derive them and a transformation function to take a stream
    of the base signals and return the transformed signals.

    Example:
    SourceSignalPair("src", signal=["sig_base", "sig_smoothed"]) would return SourceSignalPair("src", signal=["sig_base"]) and a transformation dictionary
    that maps all required base source-signals to the requested derived source-signals. transform_dict in the case above would be
    {SourceSignal("src", "sig_base"): [SourceSignal("src", "sig_base"), SourceSignal("src", "sig_smooth")]}.
    """
    base_signal_pairs: List[SourceSignalPair] = []
    derived_signal_map: Dict[SourceSignal, List[SourceSignal]] = defaultdict(list)

    for pair in source_signal_pairs:
        # Should only occur when the the source could not be found in data_source_by_id. Useful for testing with fake signal names.
        if isinstance(pair.signal, bool):
            base_signal_pairs.append(pair)
            continue

        signals = []
        for signal_name in pair.signal:
            signal = data_signals_by_key.get((pair.source, signal_name))
            if signal and signal.compute_from_base:
                derived_signal_map[SourceSignal(pair.source, signal.signal_basename)].append(SourceSignal(pair.source, signal_name))
                signals.append(signal.signal_basename)
            else:
                derived_signal_map[SourceSignal(pair.source, signal_name)].append(SourceSignal(pair.source, signal_name))
                signals.append(signal_name)
        base_signal_pairs.append(SourceSignalPair(pair.source, signals))

    return base_signal_pairs, derived_signal_map
