from dataclasses import dataclass, asdict, field
from typing import Dict, Any
from .model import DataSignal


@dataclass
class CovidcastMetaStats:
    min: float
    mean: float
    stdev: float
    max: float


@dataclass
class CovidcastMetaEntry:
    signal: DataSignal
    min_time: int
    max_time: int
    max_issue: int
    geo_types: Dict[str, CovidcastMetaStats] = field(default_factory=dict)

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
        if self.signal:
            r.update(self.signal.asdict())
        r["geo_types"] = {k: asdict(v) for k, v in self.geo_types.items()}
        return r
