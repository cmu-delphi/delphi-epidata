from dataclasses import dataclass, asdict, field
from typing import Dict, Any
from enum import Enum


class HighValuesAre(str, Enum):
    bad = "bad"
    good = "good"
    neutral = "neutral"


class SignalFormat(str, Enum):
    per100k = "per100k"
    percent = "percent"
    fraction = "fraction"
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
    if source == "safegraph" and signal.endswith("_prop"):
        return SignalFormat.per100k
    if source == "indicator-combination" and signal.endswith("_prop"):
        return SignalFormat.per100k
    return SignalFormat.raw


def guess_category(source: str, signal: str) -> SignalCategory:
    if source in ["doctor-visits"] or (source == "fb-survey" and (signal.endswith("_ili") or signal.endswith("_cli"))):
        return SignalCategory.early
    if source in ["fb-survey", "safegraph", "google-symptoms"]:
        return SignalCategory.public
    if source in ["quidel", "hospital-admissions", "indicator-combination"]:
        return SignalCategory.late
    return SignalCategory.other


@dataclass
class CovidcastMetaStats:
    min: float
    mean: float
    stdev: float
    max: float


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

    def __post_init__(self):
        # derive fields
        self.name = guess_name(self.source, self.signal)
        self.high_values_are = guess_high_values_are(self.source, self.signal)
        self.format = guess_format(self.source, self.signal)
        self.category = guess_category(self.source, self.signal)

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
