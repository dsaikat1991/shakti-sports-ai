from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class TwinSession:
    athlete_id: str
    performance_id: str
    session_id: str | None
    event: str
    recorded_at: str
    features: dict[str, float]
    confidences: dict[str, float] | None = None
    context: dict[str, Any] | None = None
    schema_version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class PersonalBaseline:
    feature_name: str
    samples: int
    mean: float
    standard_deviation: float
    minimum: float
    maximum: float
    median: float
    confidence: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class DeviationResult:
    feature_name: str
    current_value: float
    baseline_mean: float
    z_score: float | None
    deviation_percent: float | None
    classification: str
    confidence: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class TwinState:
    athlete_id: str
    event: str
    sessions_analyzed: int
    latest_performance_id: str
    latest_recorded_at: str
    baselines: dict[str, Any]
    current_deviations: dict[str, Any]
    trends: dict[str, Any]
    adaptations: dict[str, Any]
    regressions: dict[str, Any]
    fatigue_signature: dict[str, Any]
    intervention_response: dict[str, Any]
    readiness: dict[str, Any]
    identity_vector: dict[str, float]
    confidence: float | None
    version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
