from dataclasses import InitVar, dataclass, asdict, field
from typing import Dict, Any, List, Set
from enum import Enum


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


def guess_name(source: str, signal: str) -> str:
    return f"{source.upper()}: {' '.join((s.capitalize() for s in signal.split('_')))}"


def guess_high_values_are(source: str, signal: str) -> HighValuesAre:
    if signal.endswith("_ili") or signal.endswith("_wili") or signal.endswith("_cli") or signal.endswith("_wcli"):
        return HighValuesAre.bad
    if source == "chng" and signal.endswith("_covid"):
        return HighValuesAre.bad
    if source == "covid-act-now":
        if signal.endswith("_positivity_rate"):
            return HighValuesAre.bad
        if signal.endswith("_total_tests"):
            return HighValuesAre.good
    if source == "fb-survey":
        if "tested_positive" in signal:
            return HighValuesAre.bad
        if "anxious" in signal or "depressed" in signal or "felt_isolated" in signal or "worried" in signal:
            return HighValuesAre.bad
        if "hesitancy_reason" in signal or "vaccine_likely" in signal or "dontneed_reason" in signal:
            return HighValuesAre.neutral
        if "mask" in signal or "vaccine" in signal or "vaccinated" in signal:
            return HighValuesAre.good
    if source in ["quidel", "indicator-combination", "google-symptoms", "doctor-visits", "hospital-admissions", "usa-facts", "jhu-csse", "hhs"]:
        return HighValuesAre.bad

    return HighValuesAre.neutral


def guess_format(source: str, signal: str) -> SignalFormat:
    if source in ["fb-survey", "quidel", "hospital-admissions"]:
        return SignalFormat.percent
    if source == "safegraph" and (signal.endswith("_prop") or signal.endswith("_prop_7dav")):
        return SignalFormat.per100k
    if source in ["indicator-combination", "usa-facts", "jhu-csse"] and signal.endswith("_prop"):
        return SignalFormat.per100k
    if source in ["indicator-combination", "usa-facts", "jhu-csse"] and signal.endswith("_num"):
        return SignalFormat.raw_count
    if source == "covid-act-now" and signal == "pcr_specimen_positivity_rate":
        return SignalFormat.fraction
    if source == "covid-act-now" and signal == "pcr_specimen_total_tests":
        return SignalFormat.raw_count
    return SignalFormat.raw


def guess_category(source: str, signal: str) -> SignalCategory:
    if source in ["doctor-visits"] or (source == "fb-survey" and (signal.endswith("_ili") or signal.endswith("_cli"))):
        return SignalCategory.early
    if source in ["fb-survey", "safegraph", "google-symptoms"]:
        return SignalCategory.public
    if source in ["quidel", "hospital-admissions", "indicator-combination", "usa-facts", "jhu-csse", "hhs"]:
        return SignalCategory.late
    return SignalCategory.other


def guess_is_smoothed(signal: str) -> bool:
    return "smoothed_" in signal or "7dav" in signal


def guess_is_cumulative(signal: str) -> bool:
    return "cumulative_" in signal


def guess_is_weighted(source: str, signal: str) -> bool:
    if source == "fb-survey" and signal.startswith("smoothed_w"):
        rest = signal[len("smoothed_") :]
        if rest.startswith("wanted") or rest.startswith("wearing") or rest.startswith("work") or rest.startswith("worried"):
            # it is smoothed_wanted but the weighted one is smoothed_wwanted
            return False
        return True
    if source == "chng" and signal.startswith("smoothed_adj_"):
        return True
    return False


def guess_has_stderr(source: str) -> bool:
    return source in ["fb-survey", "quidel"]


def guess_has_sample_size(source: str) -> bool:
    return source in ["fb-survey", "quidel"]


@dataclass
class CovidcastMetaStats:
    min: float
    mean: float
    stdev: float
    max: float


AllSignalsMap = Dict[str, Set[str]]


def guess_related_fb_survey_like(entry: "CovidcastMetaEntry", weighted_infix: str = "w") -> Set[str]:
    # compute the plain smoothed version and go from there
    smoothed_version = entry.signal
    if entry.is_weighted:
        # guess the smoothed unweighted version
        smoothed_version = entry.signal.replace("smoothed_" + weighted_infix, "smoothed_")
    elif not entry.is_smoothed:
        smoothed_version = entry.signal.replace("raw_", "smoothed_")

    related: Set[str] = set()
    related.add(smoothed_version)

    weighted_smoothed_signal = smoothed_version.replace("smoothed_", "smoothed_" + weighted_infix)
    related.add(weighted_smoothed_signal)

    raw_signal = smoothed_version.replace("smoothed_", "raw_")
    related.add(raw_signal)

    return related


def guess_related_cases_death_like(entry: "CovidcastMetaEntry") -> Set[str]:
    if entry.is_weighted:
        return set()  # cannot handle

    base_prefix = entry.signal[0 : entry.signal.index("_")]

    related: Set[str] = set()

    for format in [SignalFormat.raw_count, SignalFormat.per100k]:
        suffix = "num" if format == SignalFormat.raw_count else "prop"
        incidence_count = f"{base_prefix}_incidence_{suffix}"
        related.add(incidence_count)
        incidence_cumulative_count = f"{base_prefix}_cumulative_{suffix}"
        related.add(incidence_cumulative_count)

        smoothed_incidence_count = f"{base_prefix}_7dav_incidence_{suffix}"
        related.add(smoothed_incidence_count)
        smoothed_incidence_cumulative_count = f"{base_prefix}_7dav_cumulative_{suffix}"
        related.add(smoothed_incidence_cumulative_count)

    return related


def guess_related_safegraph(entry: "CovidcastMetaEntry") -> Set[str]:
    if entry.is_weighted:
        return set()  # cannot handle

    if entry.signal.startswith("median_home_dwell_time"):
        return {"median_home_dwell_time", "median_home_dwell_time_7dav"}

    base_prefix = entry.signal.replace("_7dav", "").replace("_prop", "").replace("_num", "")

    related: Set[str] = set()

    for format in [SignalFormat.raw_count, SignalFormat.per100k]:
        suffix = "num" if format == SignalFormat.raw_count else "prop"
        incidence_count = f"{base_prefix}_{suffix}"
        related.add(incidence_count)

        smoothed_incidence_count = f"{base_prefix}_{suffix}_7dav"
        related.add(smoothed_incidence_count)

    return related


def guess_related_generic(entry: "CovidcastMetaEntry") -> Set[str]:
    if entry.is_weighted or entry.is_cumulative:
        return set()  # don't know
    if entry.is_smoothed:
        raw_version = entry.signal.replace("smoothed_", "raw_")
        return {raw_version}
    else:
        smoothed_version = entry.signal.replace("raw_", "smoothed_")
        return {smoothed_version}


def guess_related_signals(entry: "CovidcastMetaEntry", all_signals: AllSignalsMap) -> List[str]:
    if entry.source == "indicator-combination" and entry.signal.startswith("nmf_"):
        return []

    guesses: Set[str] = set()
    if entry.source == "fb-survey":
        guesses = guess_related_fb_survey_like(entry, "w")
    elif entry.source in ["chng", "doctor-visits", "hospital-admissions"]:
        guesses = guess_related_fb_survey_like(entry, "adj_")
    elif entry.source == "safegraph":
        guesses = guess_related_safegraph(entry)
    elif entry.source in ["indicator-combination", "usa-facts", "jhu-csse"]:
        guesses = guess_related_cases_death_like(entry)
    else:
        guesses = guess_related_generic(entry)

    # remove oneself
    guesses.discard(entry.signal)
    # return just valid signals
    same_source_signals = all_signals.get(entry.source, set())
    return sorted(guesses.intersection(same_source_signals))


@dataclass
class CovidcastMetaEntry:
    source: str
    signal: str
    min_time: int
    max_time: int
    max_issue: int
    geo_types: Dict[str, CovidcastMetaStats]

    name: str = field(init=False)
    high_values_are: HighValuesAre = field(init=False)
    format: SignalFormat = field(init=False)
    category: SignalCategory = field(init=False)
    is_smoothed: bool = field(init=False)
    is_weighted: bool = field(init=False)
    is_cumulative: bool = field(init=False)
    has_stderr: bool = field(init=False)
    has_sample_size: bool = field(init=False)

    related_signals: List[str] = field(init=False)

    all_signals: InitVar[AllSignalsMap]

    def __post_init__(self, all_signals: AllSignalsMap):
        # derive fields
        self.name = guess_name(self.source, self.signal)
        self.high_values_are = guess_high_values_are(self.source, self.signal)
        self.format = guess_format(self.source, self.signal)
        self.category = guess_category(self.source, self.signal)
        self.is_smoothed = guess_is_smoothed(self.signal)
        self.is_weighted = guess_is_weighted(self.source, self.signal)
        self.is_cumulative = guess_is_cumulative(self.signal)
        self.has_stderr = guess_has_stderr(self.source)
        self.has_sample_size = guess_has_sample_size(self.source)
        self.related_signals = guess_related_signals(self, all_signals)

    def intergrate(self, row: Dict[str, Any]):
        if row["min_time"] < self.min_time:
            self.min_time = row["min_time"]
        if row["max_time"] > self.max_time:
            self.max_time = row["max_time"]
        if row["max_issue"] > self.max_issue:
            self.max_issue = row["max_issue"]
        self.geo_types[row["geo_type"]] = CovidcastMetaStats(row["min_value"], row["mean_value"], row["stdev_value"], row["max_value"])

    def asdict(self):
        r = asdict(self)
        r["geo_types"] = {k: asdict(v) for k, v in self.geo_types.items()}
        return r
