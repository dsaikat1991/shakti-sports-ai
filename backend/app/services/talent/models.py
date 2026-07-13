from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any

@dataclass(slots=True, frozen=True)
class AthleteProfileVector:
    athlete_id: str
    event: str
    age_group: str | None
    sex: str | None
    level: str | None
    features: dict[str, float]
    confidences: dict[str, float] | None = None
    metadata: dict[str, Any] | None = None
    schema_version: str = "0.1.0"
    def to_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass(slots=True, frozen=True)
class SimilarityMatch:
    athlete_id: str
    similarity_score: float
    shared_features: tuple[str, ...]
    cohort: dict[str, Any]
    confidence: float | None
    def to_dict(self) -> dict[str, Any]:
        payload=asdict(self); payload["shared_features"]=list(self.shared_features); return payload

@dataclass(slots=True, frozen=True)
class BenchmarkMetric:
    feature_name: str
    value: float
    percentile: float
    cohort_size: int
    direction: str
    confidence: float | None
    def to_dict(self) -> dict[str, Any]: return asdict(self)
