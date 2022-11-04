from dataclasses import asdict, dataclass, field
from enum import Enum
from numbers import Number
from typing import Callable, Iterator, Optional, Dict, List, Set, Tuple, Union

from pathlib import Path
import re
from more_itertools import flatten, peekable
import pandas as pd
import numpy as np

from delphi_utils.nancodes import Nans
from ..._params import SourceSignalPair, TimePair
from .smooth_diff import generate_smoothed_rows, generate_diffed_rows
from ...utils import shift_time_value, iterate_over_ints_and_ranges


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


def reindex_iterable(iterator: Iterator[Dict], time_pairs: Optional[List[TimePair]], fill_value: Optional[Number] = None) -> Iterator[Dict]:
    """Produces an iterator that fills in gaps in the time window of another iterator.

    Used to produce an iterator with a contiguous time index for time series operations.

    We iterate over contiguous range of days made from time_pairs. If `iterator`, which is assumed to be sorted by its "time_value" key,
    is missing a time_value in the range, a row is returned with the missing date and dummy fields.
    """
    # Iterate as normal if time_pairs is empty or None.
    if not time_pairs:
        yield from iterator
        return

    _iterator = peekable(iterator)

    # If the iterator is empty, we halt immediately.
    try:
        first_item = _iterator.peek()
    except StopIteration:
        return

    _default_item = first_item.copy()
    _default_item.update({"stderr": None, "sample_size": None, "issue": None, "lag": None, "missing_stderr": Nans.NOT_APPLICABLE, "missing_sample_size": Nans.NOT_APPLICABLE})

    # Non-trivial operations otherwise.
    min_time_value = first_item.get("time_value")
    for expected_time_value in get_day_range(time_pairs):
        if expected_time_value < min_time_value:
            continue

        try:
            # This will stay the same until the peeked element is consumed.
            new_item = _iterator.peek()
        except StopIteration:
            return

        if expected_time_value == new_item.get("time_value"):
            # Get the value we just peeked.
            yield next(_iterator)
        else:
            # Return a default row instead.
            # Copy to avoid Python by-reference memory issues.
            default_item = _default_item.copy()
            default_item.update({"time_value": expected_time_value, "value": fill_value, "missing_value": Nans.NOT_MISSING if fill_value and not np.isnan(fill_value) else Nans.NOT_APPLICABLE})
            yield default_item


def is_derived(source: str, signal: Union[bool, str]) -> bool:
    """Returns a list of derived signal pairs."""
    if isinstance(signal, bool):
        return False

    data_signal = data_signals_by_key.get((source, signal))
    if data_signal and data_signal.compute_from_base and data_signal.format in [SignalFormat.raw, SignalFormat.raw_count, SignalFormat.count]:
        return True
    else:
        return False


def get_base_signal_transform(derived_source_signal_pair: SourceSignalPair) -> Tuple[SourceSignalPair, TransformType]:
    """Returns the transformation needed to get the derived signal.

    Assumed to have derived_source_signal_pair.signal be a singleton list with an actual derived signal.
    Use is_derived beforehand to determine.
    """
    derived_data_signal = data_signals_by_key.get((derived_source_signal_pair.source, derived_source_signal_pair.signal[0]))

    if not derived_data_signal:
        raise ValueError(f"Unrecognized signal {derived_data_signal}.")
    elif not derived_data_signal.compute_from_base:
        raise ValueError(f"A non-derived signal {derived_data_signal}. Verify signal is derived first.")

    base_data_signal = data_signals_by_key.get((derived_data_signal.source, derived_data_signal.signal_basename))

    if not base_data_signal:
        raise ValueError(f"The base signal could not be found for derived signal {derived_data_signal}.")

    base_source_signal_pair = SourceSignalPair(derived_data_signal.source, [derived_data_signal.signal_basename])

    # Pure incidence signal, e.g. confirmed_cumulative_num -> confirmed_incidence_num
    if base_data_signal.is_cumulative and not derived_data_signal.is_cumulative and not derived_data_signal.is_smoothed:
        transform = DIFF
    # Diffed and then smoothed signal, e.g. confirmed_cumulative_num -> confirmed_7dav_incidence_num
    elif base_data_signal.is_cumulative and not derived_data_signal.is_cumulative and derived_data_signal.is_smoothed:
        transform = DIFF_SMOOTH
    # Smoothed signal, e.g. ageusia_raw_search -> ageusia_smoothed_search
    elif not base_data_signal.is_cumulative and not derived_data_signal.is_cumulative and derived_data_signal.is_smoothed:
        transform = SMOOTH
    # Currently no signals fit this, but here for completeness.
    elif base_data_signal.is_cumulative and derived_data_signal.is_cumulative and derived_data_signal.is_smoothed:
        transform = SMOOTH
    # Something went wrong, fail gracefully.
    else:
        raise ValueError(f"Transformation couldn't be found for derived signal: {derived_source_signal_pair} with base signal: {base_source_signal_pair}")

    return base_source_signal_pair, transform


def get_pad_length(transform: TransformType, smoother_window_length: int):
    """Returns the size of the extra date padding needed, depending on the transform.

    If smoothing is required, we fetch an extra smoother_window_length - 1 days (6 by default). If both diffing and smoothing is required on the same signal,
    then we fetch extra smoother_window_length days (7 by default).
    """
    pad_length = [0]
    if DIFF_SMOOTH == transform:
        pad_length.append(smoother_window_length)
    if SMOOTH == transform:
        pad_length.append(smoother_window_length - 1)
    if DIFF == transform:
        pad_length.append(1)
    return max(pad_length)


def pad_time_pairs(time_pairs: List[TimePair], pad_length: int) -> List[TimePair]:
    """Pads a list of TimePairs with another TimePair that extends the smallest time value by the pad_length, if needed.

    Assumes day time_type, since this function is only called for JIT computations which share the same assumption.

    Example:
    [TimePair("day", [20210407])] with pad_length 6 would return [TimePair("day", [20210407]), TimePair("day", [(20210401, 20210407)])].
    """
    if pad_length < 0:
        raise ValueError("pad_length should non-negative.")
    if pad_length == 0:
        return time_pairs.copy()

    extracted_non_bool_time_values = flatten(time_pair.time_values for time_pair in time_pairs if not isinstance(time_pair.time_values, bool))
    min_time = min(time_value if isinstance(time_value, int) else time_value[0] for time_value in extracted_non_bool_time_values)

    padded_time = TimePair("day", [(shift_time_value(min_time, -1 * pad_length), min_time)])

    return time_pairs + [padded_time]


def get_day_range(time_pairs: List[TimePair]) -> Iterator[int]:
    """Iterate over a list of TimePair time_values, including the values contained in the ranges.

    Example:
    [TimePair("day", [20210407, 20210408]), TimePair("day", [20210405, (20210408, 20210411)])] would iterate over
    [20210405, 20210407, 20210408, 20210409, 20210410, 20210411].
    """
    time_values_flattened = []

    for time_pair in time_pairs:
        if time_pair.time_type != "day":
            raise ValueError("get_day_range only supports 'day' time_type.")

        if isinstance(time_pair.time_values, int):
            time_values_flattened.append(time_pair.time_values)
        elif isinstance(time_pair.time_values, list):
            time_values_flattened.extend(time_pair.time_values)
        else:
            raise ValueError("get_day_range only supports int or list time_values.")

    return iterate_over_ints_and_ranges(time_values_flattened)
