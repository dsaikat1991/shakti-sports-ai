from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any

@dataclass(slots=True, frozen=True)
class HorizontalForceFrame:
    frame_index: int
    timestamp_ms: int
    phase: str
    side: str | None
    com_velocity_x: float
    com_velocity_y: float
    com_acceleration_x: float
    com_acceleration_y: float
    trunk_angle_deg: float | None
    shin_angle_deg: float | None
    ground_contact_probability: float | None
    toe_off_probability: float | None
    contact_time_ms: float | None
    confidence: float
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(slots=True, frozen=True)
class HorizontalForceMetrics:
    phase: str
    frames_used: int
    average_horizontal_acceleration: float | None
    average_vertical_acceleration: float | None
    horizontal_force_orientation_percent: float | None
    mean_force_vector_angle_deg: float | None
    acceleration_effectiveness_score: float | None
    posture_alignment_score: float | None
    shin_alignment_score: float | None
    contact_efficiency_score: float | None
    overall_horizontal_force_score: float | None
    rating: str
    confidence: float | None
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
