from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any, Literal
OutputTier = Literal["measured", "estimated", "predictive"]
@dataclass(slots=True, frozen=True)
class MetricEstimate:
    name: str
    value: float | None
    unit: str | None
    uncertainty: float | None
    confidence: float | None
    tier: OutputTier
    method: str
    version: str
    metadata: dict[str, Any] | None = None
    def to_dict(self) -> dict[str, Any]: return asdict(self)
@dataclass(slots=True, frozen=True)
class ReliabilitySummary:
    pose_score: float | None
    motion_score: float | None
    event_score: float | None
    physics_score: float | None
    overall_score: float | None
    rating: str
    def to_dict(self) -> dict[str, Any]: return asdict(self)
