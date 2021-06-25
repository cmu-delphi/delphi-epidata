from dataclasses import asdict, dataclass, field
from typing import Callable, Optional, Dict, List, Tuple, Iterable, Union
from enum import Enum
from pathlib import Path
import re
from numpy.lib.utils import source
import pandas as pd
import numpy as np
from pandas.core import base

from ..._params import SourceSignalPair
from .smooth_diff import generate_smooth_rows, generate_row_diffs


IDENTITY = lambda rows: rows
DIFF = lambda rows: generate_row_diffs(rows)
SMOOTH = lambda rows: generate_smooth_rows(rows)
DIFF_SMOOTH = lambda rows: generate_smooth_rows(generate_row_diffs(rows))


DERIVED_SIGNALS = {
    "google-symptoms:ageusia_smoothed_search": ("google-symptoms:ageusia_raw_search", SMOOTH),
    "google-symptoms:anosmia_smoothed_search": ("google-symptoms:anosmia_raw_search", SMOOTH),
    "google-symptoms:sum_anosmia_ageusia_smoothed_search": ("google-symptoms:sum_anosmia_ageusia_raw_search", SMOOTH),
    "jhu-csse:confirmed_7dav_cumulative_num": ("jhu-csse:confirmed_cumulative_num", SMOOTH),
    "jhu-csse:confirmed_7dav_incidence_num": ("jhu-csse:confirmed_cumulative_num", DIFF_SMOOTH),
    "jhu-csse:confirmed_incidence_num": ("jhu-csse:confirmed_cumulative_num", DIFF),
    "jhu-csse:deaths_7dav_cumulative_num": ("jhu-csse:deaths_cumulative_num", SMOOTH),
    "jhu-csse:deaths_7dav_incidence_num": ("jhu-csse:deaths_cumulative_num", DIFF_SMOOTH),
    "jhu-csse:deaths_incidence_num": ("jhu-csse:deaths_cumulative_num", DIFF),
    "usafacts:confirmed_7dav_cumulative_num": ("usafacts:confirmed_cumulative_num", SMOOTH),
    "usafacts:confirmed_7dav_incidence_num": ("usafacts:confirmed_cumulative_num", DIFF_SMOOTH),
    "usafacts:confirmed_incidence_num": ("usafacts:confirmed_cumulative_num", DIFF),
    "usafacts:deaths_7dav_cumulative_num": ("usafacts:deaths_cumulative_num", SMOOTH),
    "usafacts:deaths_7dav_incidence_num": ("usafacts:deaths_cumulative_num", DIFF_SMOOTH),
    "usafacts:deaths_incidence_num": ("usafacts:deaths_cumulative_num", DIFF),
}


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


class SignalCategory(str, Enum):
    public = "public"
    early = "early"
    late = "late"
    other = "other"


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
    based_on_other: bool = False
    compute_from_base: bool = False

    def __post_init__(self):
        self.link = _fix_links(self.link)
        self.compute_from_base = True if self.source + ":" + self.signal in DERIVED_SIGNALS else self.compute_from_base

    def derive_defaults(self, map: Dict[Tuple[str, str], "DataSignal"]):
        base = map.get((self.source, self.signal_basename))
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

    def asdict(self):
        return asdict(self)

    @property
    def key(self) -> Tuple[str, str]:
        return (self.source, self.signal)

    def get_parent_pair(self):
        basename_pair = SourceSignalPair(self.source, self.signal_basename)
        return basename_pair

    def get_parent_transform(self):
        if not self.signal.is_cumulative and not self.signal.is_smoothed:
            return DIFF
        if self.signal.is_cumulative and self.signal.is_smoothed:
            return SMOOTH
        if not self.signal.is_cumulative and self.signal.is_smoothed:
            return DIFF_SMOOTH
        return IDENTITY

    def get_parent_pair_if_derivative(self):
        if self.compute_from_base:
            return data_signals_by_key((self.source, self.signal_basename))
        else:
            return self


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
    data_signals: List[DataSignal] = [DataSignal(**d) for d in data_signals_df.to_dict(orient="records")]
    data_signals_df.set_index(["source", "signal"])

    by_source_id = {d.key: d for d in data_signals}
    for ds in data_signals:
        # derive from base signal
        ds.derive_defaults(by_source_id)

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


def _get_basename_derivation(signal: DataSignal):
    basename_pair = SourceSignalPair(signal.source, signal.signal_basename)
    if not signal.is_cumulative and not signal.is_smoothed:
        return basename_pair, DIFF
    if signal.is_cumulative and signal.is_smoothed:
        return basename_pair, SMOOTH
    if not signal.is_cumulative and signal.is_smoothed:
        return basename_pair, DIFF_SMOOTH
    return basename_pair, IDENTITY


def _resolve_all_signals(source_signal_pair: SourceSignalPair) -> SourceSignalPair:
    if source_signal_pair.signal == True:
        source = data_sources_by_id.get(source_signal_pair.source)
        if source:
            return SourceSignalPair(source.source, [s.signal for s in source.signals])
    return source_signal_pair


def _convert_pair_list_to_pair(source_signal_pairs: List[SourceSignalPair]) -> SourceSignalPair:
    if len({pair.source for pair in source_signal_pairs}) == 1:
        return SourceSignalPair(source_signal_pairs[0].source, [pair.signal for pair in source_signal_pairs])
    else:
        raise ValueError("The signal pairs don't share the same source.")


def create_source_signal_derivation_mapper(source_signals: List[SourceSignalPair]) -> Tuple[List[SourceSignalPair], Dict]:
    transformed_pairs: List[SourceSignalPair] = []
    source_signals = [_resolve_all_signals(pair) for pair in source_signals]

    for pair in source_signals:
        if not isinstance(pair.signal, tuple):
            signal = data_signals_by_key.get(pair.astuple())
            if signal and signal.compute_from_base:
                transformed_pairs.append(signal.get_parent_pair())
            else:
                transformed_pairs.append(pair)
        else:
            source_signals_ = []
            for signal_ in pair.signal:
                source_signals_ = [data_signals_by_key.get((pair.source, signal_.signal)) if data_signals_by_key.get((pair.source, signal_.signal)) is not None else  ]

            if signal and signal.compute_from_base:
                source_signals_.append(signal.get_parent_pair())
            else:
                source_signals_.append(pair)

    # TODO: Figure out if we need to map back
    def map_group(source: str, signal: str, group: Iterable[Dict]) -> Iterable[Dict]:
        """
        maps a given row source back to its alias version
        """
        signal_ = data_signals_by_key.get((source, signal))
        if signal_:
            transform = signal_.get_parent_transform()
            return transform(group)
        return group

    return transformed_pairs, map_group


def fetch_derivable_signal(source_signal_pair: SourceSignalPair) -> Tuple[SourceSignalPair, Callable]:
    """Fetch raw version of a signal, if available, for smoothing."""
    source_signal_name = source_signal_pair.source + ":" + source_signal_pair.signal
    try:
        raw_source_signal, transform = DERIVED_SIGNALS[source_signal_name]
        raw_source, raw_signal = raw_source_signal.split(":")
        return SourceSignalPair(raw_source, raw_signal), transform
    except KeyError:
        return source_signal_pair, IDENTITY


def fetch_derivable_signals(source_signal_pairs: List[SourceSignalPair]) -> Dict[str, Tuple[SourceSignalPair, Callable]]:
    signals_and_transforms = [fetch_derivable_signal(source_signal_pair) for source_signal_pair in source_signal_pairs]
    signals_and_transforms_dict = {source_signal_pair.source + ":" + source_signal_pair.signal: transform for source_signal_pair, transform in signals_and_transforms}
    return signals_and_transforms_dict
