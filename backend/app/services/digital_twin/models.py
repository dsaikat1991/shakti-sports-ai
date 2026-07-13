from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class AthleteMetricSnapshot:
    athlete_id: str
    performance_id: str
    session_id: str | None
    event: str
    recorded_at: str
    metrics: dict[str, float]
    confidences: dict[str, float] | None = None
    metadata: dict[str, Any] | None = None
    schema_version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class MetricTrend:
    metric_name: str
    samples: int
    first_value: float | None
    latest_value: float | None
    absolute_change: float | None
    percent_change: float | None
    slope_per_session: float | None
    coefficient_of_variation_percent: float | None
    direction: str
    confidence: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class PersonalBest:
    metric_name: str
    value: float
    performance_id: str
    recorded_at: str
    objective: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
