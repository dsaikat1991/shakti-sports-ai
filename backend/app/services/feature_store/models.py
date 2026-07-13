from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


FeatureTier = Literal[
    "measured",
    "estimated",
    "predictive",
]


@dataclass(slots=True, frozen=True)
class FeatureValue:
    name: str
    value: float | int | str | bool | None
    unit: str | None
    tier: FeatureTier
    confidence: float | None
    uncertainty: float | None
    source_stage: str
    method: str
    version: str
    timestamp_ms: int | None = None
    side: str | None = None
    phase: str | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class FeatureRecord:
    athlete_id: str | None
    performance_id: str
    event: str
    session_id: str | None
    feature: FeatureValue
    schema_version: str = "0.1.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "athlete_id": self.athlete_id,
            "performance_id": self.performance_id,
            "event": self.event,
            "session_id": self.session_id,
            "feature": self.feature.to_dict(),
            "schema_version": self.schema_version,
        }
