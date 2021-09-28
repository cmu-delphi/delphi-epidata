from dataclasses import asdict, dataclass, field
from enum import Enum
from functools import partial
from itertools import groupby, repeat, tee
from typing import Callable, Generator, Optional, Dict, List, Set, Tuple, Iterable, Union
from pathlib import Path
import re
from more_itertools import interleave_longest, peekable
import pandas as pd
import numpy as np

from delphi_utils.nancodes import Nans
from ..._params import SourceSignalPair, TimePair
from .smooth_diff import generate_smooth_rows, generate_row_diffs
from ...utils import time_value_range, shift_time_value


IDENTITY: Callable = lambda rows, **kwargs: rows
DIFF: Callable = lambda rows, **kwargs: generate_row_diffs(rows, **kwargs)
SMOOTH: Callable = lambda rows, **kwargs: generate_smooth_rows(rows, **kwargs)
DIFF_SMOOTH: Callable = lambda rows, **kwargs: generate_smooth_rows(generate_row_diffs(rows, **kwargs), **kwargs)


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

    reg = re.compile("\[(.+)\]\s*\((.*)\)")

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


def get_related_signals(signal: DataSignal) -> List[DataSignal]:
    return [s for s in data_signals if s != signal and s.signal_basename == signal.signal_basename]


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
        if pair.signal == True:
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


def _resolve_all_signals(source_signals: Union[SourceSignalPair, List[SourceSignalPair]], data_sources_by_id: Dict[str, DataSource]) -> Union[SourceSignalPair, List[SourceSignalPair]]:
    """Expand a request for all signals to an explicit list of signal names.

    Example: SourceSignalPair("jhu-csse", signal=True) would return SourceSignalPair("jhu-csse", [<list of all JHU signals>]).
    """
    if isinstance(source_signals, SourceSignalPair):
        if source_signals.signal == True:
            source = data_sources_by_id.get(source_signals.source)
            if source:
                return SourceSignalPair(source.source, [s.signal for s in source.signals])
        return source_signals
    if isinstance(source_signals, list):
        return [_resolve_all_signals(pair, data_sources_by_id) for pair in source_signals]
    raise TypeError("source_signals is not Union[SourceSignalPair, List[SourceSignalPair]].")


def _reindex_iterable(iterable: Iterable[Dict], time_pairs: List[TimePair], fill_value: Optional[int] = None) -> Iterable:
    """Produces an iterable that fills in gaps in the time window of another iterable.

    Used to produce an iterable with a contiguous time index for time series operations.

    We iterate over contiguous range of days made from time_pairs. If `iterable`, which is assumed to be sorted by its "time_value" key,
    is missing a time_value in the range, a dummy row entry is returned with the correct date and the value fields set appropriately.
    """
    if time_pairs is None:
        return iterable

    _iterable = peekable(iterable)
    first_item = _iterable.peek()
    day_range_index = get_day_range(time_pairs)
    for day in day_range_index.time_values:
        index_item = first_item.copy()
        index_item.update({
            "time_value": day,
            "value": fill_value,
            "stderr": None,
            "sample_size": None,
            "missing_value": Nans.NOT_MISSING if fill_value is not None else Nans.NOT_APPLICABLE,
            "missing_stderr": Nans.NOT_APPLICABLE,
            "missing_sample_size": Nans.NOT_APPLICABLE
        })
        new_item = _iterable.peek(default=index_item)
        if day == new_item.get("time_value"):
            yield next(_iterable, index_item)
        else:
            yield index_item


def _get_base_signal_transform(signal: Union[DataSignal, Tuple[str, str]], data_signals_by_key: Dict[Tuple[str, str], DataSignal] = data_signals_by_key) -> Callable:
    """Given a DataSignal, return the transformation that needs to be applied to its base signal to derive the signal."""
    if isinstance(signal, DataSignal):
        parent_signal = data_signals_by_key.get((signal.source, signal.signal_basename))
        if signal.format not in [SignalFormat.raw, SignalFormat.raw_count, SignalFormat.count] or not signal.compute_from_base or not parent_signal:
            return IDENTITY
        if signal.is_cumulative and signal.is_smoothed:
            return SMOOTH
        if not signal.is_cumulative and not signal.is_smoothed:
            return DIFF if parent_signal.is_cumulative else IDENTITY
        if not signal.is_cumulative and signal.is_smoothed:
            return DIFF_SMOOTH if parent_signal.is_cumulative else SMOOTH
        return IDENTITY
    if isinstance(signal, tuple):
        signal = data_signals_by_key.get(signal)
        if signal:
            return _get_base_signal_transform(signal, data_signals_by_key)
        return IDENTITY

    raise TypeError("signal must be either Tuple[str, str] or DataSignal.")


def get_transform_types(source_signal_pairs: List[SourceSignalPair], data_sources_by_id: Dict[str, DataSource] = data_sources_by_id, data_signals_by_key: Dict[Tuple[str, str], DataSignal] = data_signals_by_key) -> Set[Callable]:
    """Return a collection of the unique transforms required for transforming a given source-signal pair list.

    Example:
    SourceSignalPair("src", ["sig", "sig_smoothed", "sig_diff"]) would return {IDENTITY, SMOOTH, DIFF}.

    Used to pad the user DB query with extra days.
    """
    source_signal_pairs = _resolve_all_signals(source_signal_pairs, data_sources_by_id)

    transform_types = set()
    for source_signal_pair in source_signal_pairs:
        source_name = source_signal_pair.source
        signal_names = source_signal_pair.signal
        if isinstance(signal_names, bool):
            continue
        transform_types |= {_get_base_signal_transform((source_name, signal_name), data_signals_by_key=data_signals_by_key) for signal_name in signal_names}

    return transform_types


def get_pad_length(source_signal_pairs: List[SourceSignalPair], smoother_window_length: int, data_sources_by_id: Dict[str, DataSource] = data_sources_by_id, data_signals_by_key: Dict[Tuple[str, str], DataSignal] = data_signals_by_key):
    """Returns the size of the extra date padding needed, depending on the transformations the source-signal pair list requires.

    Example:
    If smoothing is required, we fetch an extra 6 days. If both diffing and smoothing is required on the same signal, then we fetch 7 extra days.

    Used to pad the user DB query with extra days.
    """
    transform_types = get_transform_types(source_signal_pairs, data_sources_by_id=data_sources_by_id, data_signals_by_key=data_signals_by_key)
    pad_length = [0]
    if DIFF_SMOOTH in transform_types:
        pad_length.append(smoother_window_length)
    if SMOOTH in transform_types:
        pad_length.append(smoother_window_length - 1)
    if DIFF in transform_types:
        pad_length.append(1)
    return max(pad_length)


def pad_time_pairs(time_pairs: List[TimePair], pad_length: int) -> List[TimePair]:
    """Pads a list of TimePairs with another TimePair that extends the smallest time value by the pad_length, if needed.

    Example:
    [TimePair("day", [20210407])] with pad_length 6 would return [TimePair("day", [20210407]), TimePair("day", [(20210401, 20210407)])].

    Used to pad the user DB query with extra days.
    """
    if pad_length < 0:
        raise ValueError("pad_length should non-negative.")
    if pad_length == 0:
        return time_pairs.copy()
    min_time = min(time_value if isinstance(time_value, int) else time_value[0] for time_pair in time_pairs if not isinstance(time_pair.time_values, bool) for time_value in time_pair.time_values)
    padded_time = TimePair("day", [(shift_time_value(min_time, -1 * pad_length), min_time)])
    new_time_pairs = time_pairs.copy()
    new_time_pairs.append(padded_time)
    return new_time_pairs


def pad_time_window(time_window: Tuple[int, int], pad_length: int) -> Tuple[int, int]:
    """Extend a time window on the left by pad_length.

    Example:
    (20210407, 20210413) with pad_length 6 would return (20210401, 20210413).

    Used to pad the user DB query with extra days.
    """
    if pad_length < 0:
        raise ValueError("pad_length should non-negative.")
    if pad_length == 0:
        return time_window
    min_time, max_time = time_window
    return (shift_time_value(min_time, -1 * pad_length), max_time)


def get_day_range(time_pairs: Union[TimePair, List[TimePair]]) -> TimePair:
    """Combine a list of TimePairs into a single contiguous, explicit TimePair object.

    Example:
    [TimePair("day", [20210407, 20210408]), TimePair("day", [(20210408, 20210410)])] would return
    TimePair("day", [20210407, 20210408, 20210409, 20210410]).

    Used to produce a contiguous time index for time series operations.
    """
    if isinstance(time_pairs, TimePair):
        time_pair = time_pairs
        time_values = sorted(list(set().union(*(set(time_value_range(time_value)) if isinstance(time_value, tuple) else {time_value} for time_value in time_pair.time_values))))
        if True in time_values:
            raise ValueError("TimePair.time_value should not be a bool when calling get_day_range.")
        return TimePair(time_pair.time_type, time_values)
    elif isinstance(time_pairs, list):
        if not all(time_pair.time_type == "day" for time_pair in time_pairs):
            raise ValueError("get_day_range only supports day time_type pairs.")
        time_values = sorted(list(set().union(*(get_day_range(time_pair).time_values for time_pair in time_pairs))))
        return TimePair("day", time_values)
    else:
        raise ValueError("get_day_range received an unsupported type as input.")


def _generate_transformed_rows(
    parsed_rows: Iterable[Dict], time_pairs: Optional[List[TimePair]] = None, transform_dict: Optional[Dict[Tuple[str, str], List[Tuple[str, str]]]] = None, transform_args: Optional[Dict] = None, group_keyfunc: Optional[Callable] = None, data_signals_by_key: Dict[Tuple[str, str], DataSignal] = data_signals_by_key,
) -> Iterable[Dict]:
    """Applies time-series transformations to streamed rows from a database.

    Parameters:
    parsed_rows: Iterable[Dict]
        Streamed rows from the database.
    time_pairs: Optional[List[TimePair]], default None
        A list of TimePairs, which can be used to create a continguous time index for time-series operations.
        The min and max dates in the TimePairs list is used.
    transform_dict: Optional[Dict[Tuple[str, str], List[Tuple[str, str]]]], default None
        A dictionary mapping base sources to a list of their derived signals that the user wishes to query.
        For example, transform_dict may be {("jhu-csse", "confirmed_cumulative_num): [("jhu-csse", "confirmed_incidence_num"), ("jhu-csse", "confirmed_7dav_incidence_num")]}.
    transform_args: Optional[Dict], default None
        A dictionary of keyword arguments for the transformer functions.
    group_keyfunc: Optional[Callable], default None
        The groupby function to use to order the streamed rows. Note that Python groupby does not do any sorting, so
        parsed_rows are assumed to be sorted in accord with this groupby.
    data_signals_by_key: Dict[Tuple[str, str], DataSignal], default data_signals_by_key
        The dictionary of DataSignals which is used to find the base signal transforms

    Yields:
    transformed rows: Dict
        The transformed rows returned in an interleaved fashion. Non-transformed rows have the IDENTITY operation applied.
    """
    if not transform_args:
        transform_args = dict()
    if not transform_dict:
        transform_dict = dict()
    if not group_keyfunc:
        group_keyfunc = lambda row: (row["geo_type"], row["geo_value"], row["source"], row["signal"])

    try:
        for key, group in groupby(parsed_rows, group_keyfunc):
            _, _, source_name, signal_name = key
            # Extract the list of derived signals.
            derived_signals: List[Tuple[str, str]] = transform_dict.get((source_name, signal_name), [(source_name, signal_name)])
            # Create a list of source-signal pairs along with the transformation required for the signal.
            source_signal_pairs_and_group_transforms: List[Tuple[Tuple[str, str], Callable]] = [((derived_source, derived_signal), _get_base_signal_transform((derived_source, derived_signal), data_signals_by_key)) for (derived_source, derived_signal) in derived_signals]
            # Put the current time series on a contiguous time index.
            group_continguous_time = _reindex_iterable(group, time_pairs, fill_value=transform_args.get("pad_fill_value")) if time_pairs else group
            # Create copies of the iterable, with smart memory usage.
            group_iter_copies: Iterable[Iterable[Dict]] = tee(group_continguous_time, len(source_signal_pairs_and_group_transforms))
            # Create a list of transformed group iterables, remembering their derived name as needed.
            transformed_group_rows: Iterable[Iterable[Dict]] = (zip(transform(rows, **transform_args), repeat(key)) for (key, transform), rows in zip(source_signal_pairs_and_group_transforms, group_iter_copies))
            # Traverse through the transformed iterables in an interleaved fashion, which makes sure that only a small window
            # of the original iterable (group) is stored in memory.
            for row, (_, derived_signal) in interleave_longest(*transformed_group_rows):
                row["signal"] = derived_signal
                yield row
    except Exception as e:
        print(f"Tranformation encountered error of type {type(e)}, with message {e}. Yielding None and stopping.")
        yield None


def get_basename_signals(source_signal_pairs: List[SourceSignalPair], data_sources_by_id: Dict[str, DataSource] = data_sources_by_id, data_signals_by_key: Dict[Tuple[str, str], DataSignal] = data_signals_by_key) -> Tuple[List[SourceSignalPair], Generator]:
    """From a list of SourceSignalPairs, return the base signals required to derive them and a transformation function to take a stream
    of the base signals and return the transformed signals.

    Example:
    SourceSignalPair("src", signal=["sig_base", "sig_smoothed"]) would return SourceSignalPair("src", signal=["sig_base"]) and a transformation function
    that will take the returned database query for "sig_base" and return both the base time series and the smoothed time series.
    """
    source_signal_pairs = _resolve_all_signals(source_signal_pairs, data_sources_by_id)
    base_signal_pairs: List[SourceSignalPair] = []
    transform_dict: Dict[Tuple[str, str], List[Tuple[str, str]]] = dict()

    for pair in source_signal_pairs:
        if isinstance(pair.signal, bool):
            base_signal_pairs.append(pair)
            continue

        source_name = pair.source
        signal_names = pair.signal
        signals = []
        for signal_name in signal_names:
            signal = data_signals_by_key.get((source_name, signal_name))
            if not signal or not signal.compute_from_base:
                signals.append(signal_name)
                transform_dict.setdefault((source_name, signal_name), []).append((source_name, signal_name))
            else:
                signals.append(signal.signal_basename)
                transform_dict.setdefault((source_name, signal.signal_basename), []).append((source_name, signal_name))
        base_signal_pairs.append(SourceSignalPair(pair.source, signals))

    row_transform_generator = partial(_generate_transformed_rows, transform_dict=transform_dict, data_signals_by_key=data_signals_by_key)

    return base_signal_pairs, row_transform_generator
