from collections import Counter
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Callable, Generator, Optional, Dict, List, Set, Tuple, Iterable, Counter, Union
from pathlib import Path
import re
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame

from ..._params import SourceSignalPair
from .smooth_diff import generate_smooth_rows, generate_row_diffs


IDENTITY = lambda rows: rows
DIFF = lambda rows, **kwargs: generate_row_diffs(rows, **kwargs)
SMOOTH = lambda rows, **kwargs: generate_smooth_rows(rows, **kwargs)
DIFF_SMOOTH = lambda rows, **kwargs: generate_smooth_rows(generate_row_diffs(rows, **kwargs), **kwargs)


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
    active: bool
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


def get_related_signals(signal: DataSignal) -> List[DataSignal]:
    return [s for s in data_signals if s != signal and s.signal_basename == signal.signal_basename]


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


def _resolve_all_signals(source_signals: Union[SourceSignalPair, List[SourceSignalPair]]) -> Union[SourceSignalPair, List[SourceSignalPair]]:
    if isinstance(source_signals, SourceSignalPair):
        if source_signals.signal == True:
            source = data_sources_by_id.get(source_signals.source)
            if source:
                return SourceSignalPair(source.source, [s.signal for s in source.signals])
        return source_signals
    if isinstance(source_signals, list):
        return [_resolve_all_signals(pair) for pair in source_signals]
    raise TypeError("source_signals is not Union[SourceSignalPair, List[SourceSignalPair]].")


def _get_parent_signal(signal: DataSignal, data_signals_by_key: DataFrame) -> DataSignal:
    parent_signal = data_signals_by_key.get((signal.source, signal.signal_basename))
    if parent_signal:
        return parent_signal
    return signal


def _get_parent_transform(signal: DataSignal, data_signals_by_key: DataFrame) -> Callable:
    if signal.format not in [SignalFormat.raw, SignalFormat.raw_count, SignalFormat.count]:
        return IDENTITY

    parent_signal = _get_parent_signal(signal, data_signals_by_key)
    if signal.is_cumulative and signal.is_smoothed:
        return SMOOTH
    if not signal.is_cumulative and not signal.is_smoothed:
        return DIFF if parent_signal.is_cumulative else IDENTITY
    if not signal.is_cumulative and signal.is_smoothed:
        return DIFF_SMOOTH if parent_signal.is_cumulative else SMOOTH
    return IDENTITY


def _get_signal_counts(source_signal_pairs: List[SourceSignalPair]) -> Counter[Tuple[str, str]]:
    """Count source-signal pair occurrences.

    Assumes a reduced List[SourceSignalPair] from _params._combine_source_signal_pairs.
    Returns a Counter keyed by (source, signal) tuples.
    """
    counts: Counter[Tuple[str, str]] = Counter()

    for source_signal_pair in source_signal_pairs:
        source, signals = source_signal_pair.source, source_signal_pair.signal
        if isinstance(signals, bool):
            continue
        counts += Counter([(source, signal) for signal in signals])

    return counts


def _buffer_and_tag_iterator(it: Iterable[Dict], counts: Counter, key_prop: Callable) -> Iterable[Dict]:
    """Buffer an iterator for repeated passes.

    Parameters
    ----------
    it: Iterable[Dict]
        The iterator of dictionaries.
    counts: Counter
        A Counter object taking keys from key_prop and returning the number of times to run through each
        iterable with the key_prop value. E.g. each iterable is a row value for a signal and the Counter keys
        are (source, signal) tuples.
    key_prop: Callable
        A function taking an element of the iterator and returning a key of the counts. Used to identify
        elements and store them in the buffer if needed.

    Returns
    ----------
    An iterator that runs through the iterator at least once and repeats other values as specified by counts.
    Additionally, sets the value of the "_tag" key for every Dict in the iterator according to the number of
    times the given sequence of iterable values have been repeated (starting from 0).
    """
    buffer = {}
    # First iterator pass.
    for x in it:
        key = key_prop(x)
        if counts.get(key) is not None and counts[key] > 1:
            buffer.setdefault(key, []).append(x)
        x["_tag"] = 0
        yield x

    # Buffer pass as needed.
    for key in buffer:
        for i in range(counts[key]-1):
            for x in buffer[key]:
                x = x.copy()
                x["_tag"] = i + 1
                yield x


def create_source_signal_group_transform_mapper(source_signals: List[SourceSignalPair]) -> Tuple[List[SourceSignalPair], Dict]:
    # This should resolve ("source", True) pairs to signal lists, except for sources not present in data_signals_by_key.
    source_signals = _resolve_all_signals(source_signals)
    transformed_pairs: List[SourceSignalPair] = []
    transform_dict: Dict[Tuple[str, str, int], Callable] = {}
    alias_to_data_signals: Dict[Tuple[str, str, int], str] = {}

    for pair in source_signals:
        source_name: str = pair.source
        signals: List[str] = []

        if isinstance(pair.signal, bool):
            transformed_pairs.append(pair)
            continue

        for i, signal_name in enumerate(pair.signal):
            signal: DataSignal = data_signals_by_key.get((source_name, signal_name))
            if not signal or not signal.compute_from_base:
                signals.append(signal_name)
                continue

            signals.append(signal.signal_basename)
            transform_dict[(source_name, signal.signal_basename, i)] = _get_parent_transform(signal, data_signals_by_key)
            alias_to_data_signals[(source_name, signal.signal_basename, i)] = signal_name
        transformed_pairs.append(SourceSignalPair(pair.source, signals))

    # Given a (source, signal, tag) tuple and the grouped-by Iterable[Dict] of that source-signal's rows
    # returns a transformed version of the rows (transforming the rows to what the user requested).
    # E.g. the tuple ('jhu-csse', 'confirmed_cumulative_num', 1) may return a differenced version of the same signal
    # if the user originally requested ('jhu-csse', 'incidence_cumulative_num').
    def transform_group(source: str, signal: str, tag: int, group: Iterable[Dict], **kwargs) -> Iterable[Dict]:
        transform: Callable = transform_dict.get((source, signal, tag))
        if transform:
            return transform(group, **kwargs)
        return group

    # Given a (source, signal, tag) tuple, returns the original user request signal name.
    # E.g. the tuple ('jhu-csse', 'confirmed_cumulative_num', 1) may return 'incidence_cumulative_num'
    # if the user originally requested ('jhu-csse', 'incidence_cumulative_num').
    def map_row(source: str, signal: str, tag: int) -> str:
        """
        maps a given row source back to its alias version
        """
        return alias_to_data_signals.setdefault((source, signal, tag), signal)

    # Return a dictionary of the number of signal repeats in a List[SourceSignalPairs]. Used by
    # _buffer_and_tag_iterator in the covidcast endpoint.
    counts: Counter = _get_signal_counts(source_signals)
    iterator_buffer: Generator = lambda x, y: _buffer_and_tag_iterator(x, counts, y)

    return transformed_pairs, transform_group, map_row, iterator_buffer
