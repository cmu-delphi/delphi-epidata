from dataclasses import asdict, dataclass, field
from datetime import timedelta
from enum import Enum
from functools import partial
from itertools import groupby, tee
from numbers import Number
from typing import Callable, Generator, Iterator, Optional, Dict, List, Set, Tuple, Union

from pathlib import Path
import re
import pandas as pd
import numpy as np

from delphi_utils.nancodes import Nans
from ..._params import SourceSignalPair, TimePair
from .smooth_diff import generate_smoothed_rows, generate_diffed_rows
from ...utils import shift_day_value, day_to_time_value, time_value_to_day


PANDAS_DTYPES = {
    "source": str,
    "signal": str,
    "time_type": str,
    "time_value": "Int64",
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

IDENTITY: Callable = lambda rows, **kwargs: rows
DIFF: Callable = lambda rows, **kwargs: generate_diffed_rows(rows, **kwargs)
SMOOTH: Callable = lambda rows, **kwargs: generate_smoothed_rows(rows, **kwargs)
DIFF_SMOOTH: Callable = lambda rows, **kwargs: generate_smoothed_rows(generate_diffed_rows(rows, **kwargs), **kwargs)

SignalTransforms = Dict[SourceSignalPair, SourceSignalPair]
TransformType = Callable[[Iterator[Dict]], Iterator[Dict]]

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


def _reindex_iterable(iterator: Iterator[Dict], fill_value: Optional[Number] = None) -> Iterator[Dict]:
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


def _get_base_signal_transform(signal: Union[DataSignal, Tuple[str, str]]) -> Callable:
    """Given a DataSignal, return the transformation that needs to be applied to its base signal to derive the signal."""
    if isinstance(signal, DataSignal):
        base_signal = data_signals_by_key.get((signal.source, signal.signal_basename))
        if signal.format not in [SignalFormat.raw, SignalFormat.raw_count, SignalFormat.count] or not signal.compute_from_base or not base_signal:
            return IDENTITY
        if signal.is_cumulative and signal.is_smoothed:
            return SMOOTH
        if not signal.is_cumulative and not signal.is_smoothed:
            return DIFF if base_signal.is_cumulative else IDENTITY
        if not signal.is_cumulative and signal.is_smoothed:
            return DIFF_SMOOTH if base_signal.is_cumulative else SMOOTH
        return IDENTITY

    if isinstance(signal, tuple):
        if signal := data_signals_by_key.get(signal):
            return _get_base_signal_transform(signal)
        return IDENTITY

    raise TypeError("signal must be either Tuple[str, str] or DataSignal.")


def get_transform_types(source_signal_pairs: List[SourceSignalPair]) -> Set[Callable]:
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

        transform_types |= {_get_base_signal_transform((source_name, signal_name)) for signal_name in signal_names}

    return transform_types


def get_pad_length(source_signal_pairs: List[SourceSignalPair], smoother_window_length: int):
    """Returns the size of the extra date padding needed, depending on the transformations the source-signal pair list requires.

    If smoothing is required, we fetch an extra smoother_window_length - 1 days (6 by default). If both diffing and smoothing is required on the same signal,
    then we fetch extra smoother_window_length days (7 by default).

    Used to pad the user DB query with extra days.
    """
    transform_types = get_transform_types(source_signal_pairs)
    pad_length = [0]
    if DIFF_SMOOTH in transform_types:
        pad_length.append(smoother_window_length)
    if SMOOTH in transform_types:
        pad_length.append(smoother_window_length - 1)
    if DIFF in transform_types:
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


def _generate_transformed_rows(
    parsed_rows: Iterator[Dict],
    transform_dict: Optional[SignalTransforms] = None,
    transform_args: Optional[Dict] = None,
    group_keyfunc: Optional[Callable] = None,
) -> Iterator[Dict]:
    """Applies time-series transformations to streamed rows from a database.

    Parameters:
    parsed_rows: Iterator[Dict]
        An iterator streaming rows from a database query. Assumed to be sorted by source, signal, geo_type, geo_value, time_type, and time_value.
    transform_dict: Optional[SignalTransforms], default None
        A dictionary mapping base sources to a list of their derived signals that the user wishes to query.
        For example, transform_dict may be {("jhu-csse", "confirmed_cumulative_num): [("jhu-csse", "confirmed_incidence_num"), ("jhu-csse", "confirmed_7dav_incidence_num")]}.
    transform_args: Optional[Dict], default None
        A dictionary of keyword arguments for the transformer functions.
    group_keyfunc: Optional[Callable], default None
        The groupby function to use to order the streamed rows. Note that Python groupby does not do any sorting, so
        parsed_rows are assumed to be sorted in accord with this groupby.

    Yields:
    transformed rows: Dict
        The transformed rows returned in an interleaved fashion. Non-transformed rows have the IDENTITY operation applied.
    """
    if not transform_args:
        transform_args = dict()
    if not transform_dict:
        transform_dict = dict()
    if not group_keyfunc:
        group_keyfunc = lambda row: (row["source"], row["signal"], row["geo_type"], row["geo_value"])

    for key, source_signal_geo_rows in groupby(parsed_rows, group_keyfunc):
        base_source_name, base_signal_name, _, _ = key
        # Extract the list of derived signals; if a signal is not in the dictionary, then use the identity map.
        derived_signals: SourceSignalPair = transform_dict.get(SourceSignalPair(base_source_name, [base_signal_name]), SourceSignalPair(base_source_name, [base_signal_name]))
        # Speed up base signals by not transforming them.
        if derived_signals.signal == [base_signal_name]:
            yield from source_signal_geo_rows
            continue
        # Create a list of source-signal pairs along with the transformation required for the signal.
        signal_names_and_transforms: List[Tuple[Tuple[str, str], Callable]] = [(derived_signal, _get_base_signal_transform((base_source_name, derived_signal))) for derived_signal in derived_signals.signal]
        # Put the current time series on a contiguous time index.
        source_signal_geo_rows = _reindex_iterable(source_signal_geo_rows, fill_value=transform_args.get("pad_fill_value"))
        # Create copies of the iterable, with smart memory usage.
        source_signal_geo_rows_copies: Iterator[Iterator[Dict]] = tee(source_signal_geo_rows, len(signal_names_and_transforms))
        # Create a list of transformed group iterables, remembering their derived name as needed.
        transformed_signals_iterators: List[Tuple[str, Iterator[Dict]]] = [(derived_signal, transform(rows, **transform_args)) for (derived_signal, transform), rows in zip(signal_names_and_transforms, source_signal_geo_rows_copies)]
 
        # Traverse through the transformed iterables in an interleaved fashion, which makes sure that only a small window
        # of the original iterable (group) is stored in memory.
        while transformed_signals_iterators:
            for derived_signal_name, transformed_signal_iterator in transformed_signals_iterators:
                try:
                    row = next(transformed_signal_iterator)
                    row["signal"] = derived_signal_name
                    yield row
                except StopIteration:
                    transformed_signals_iterators.remove((derived_signal_name, transformed_signal_iterator))


def get_basename_signal_and_jit_generator(source_signal_pairs: List[SourceSignalPair], transform_args: Optional[Dict[str, Union[str, int]]] = None) -> Tuple[List[SourceSignalPair], Generator]:
    """From a list of SourceSignalPairs, return the base signals required to derive them and a transformation function to take a stream
    of the base signals and return the transformed signals.

    Example:
    SourceSignalPair("src", signal=["sig_base", "sig_smoothed"]) would return SourceSignalPair("src", signal=["sig_base"]) and a transformation function
    that will take the returned database query for "sig_base" and return both the base time series and the smoothed time series. transform_dict in this case
    would be {("src", "sig_base"): [("src", "sig_base"), ("src", "sig_smooth")]}.
    """
    base_signal_pairs: List[SourceSignalPair] = []
    transform_dict: SignalTransforms = dict()

    for pair in source_signal_pairs:
        # Should only occur when the SourceSignalPair was unrecognized by _resolve_bool_source_signals. Useful for testing with fake signal names.
        if isinstance(pair.signal, bool):
            base_signal_pairs.append(pair)
            continue

        signals = []
        for signal_name in pair.signal:
            signal = data_signals_by_key.get((pair.source, signal_name))
            if not signal or not signal.compute_from_base:
                transform_dict.setdefault(SourceSignalPair(source=pair.source, signal=[signal_name]), SourceSignalPair(source=pair.source, signal=[])).add_signal(signal_name)
                signals.append(signal_name)
            else:
                transform_dict.setdefault(SourceSignalPair(source=pair.source, signal=[signal.signal_basename]), SourceSignalPair(source=pair.source, signal=[])).add_signal(signal_name)
                signals.append(signal.signal_basename)
        base_signal_pairs.append(SourceSignalPair(pair.source, signals))

    row_transform_generator = partial(_generate_transformed_rows, transform_dict=transform_dict, transform_args=transform_args)

    return base_signal_pairs, row_transform_generator
