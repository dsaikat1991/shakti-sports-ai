from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class LegSpringFrame:
    frame_index: int
    timestamp_ms: int
    side: str
    phase: str

    com_y: float
    hip_y: float
    knee_y: float
    ankle_y: float
    foot_y: float

    contact_probability: float
    toe_off_probability: float | None

    ground_contact_ms: float | None
    flight_time_ms: float | None
    cadence_spm: float | None

    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class LegSpringMetrics:
    side: str
    phase: str
    frames_used: int

    estimated_leg_compression_normalized: float | None
    elastic_return_ratio: float | None
    dynamic_leg_stiffness_index: float | None
    reactive_compression_score: float | None
    elastic_recovery_timing_percent: float | None
    contact_compression_rate: float | None
    vertical_bounce_efficiency_score: float | None
    spring_stability_score: float | None
    overall_leg_spring_score: float | None

    rating: str
    confidence: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
