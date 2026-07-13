from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class AthleteSessionProfile:
    athlete_id: str
    performance_id: str
    recorded_at: str
    event: str
    features: dict[str, float]
    confidences: dict[str, float] | None = None
    metadata: dict[str, Any] | None = None
    schema_version: str = "0.1.0"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class RankedFeature:
    feature_name: str
    value: float
    score: float
    confidence: float | None
    category: str
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class AthleteFingerprint:
    athlete_id: str
    event: str
    vector: dict[str, float]
    dominant_traits: tuple[str, ...]
    confidence: float | None
    version: str = "0.1.0"

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["dominant_traits"] = list(self.dominant_traits)
        return result
