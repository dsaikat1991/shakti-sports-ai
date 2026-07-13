from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class ContactMotionFrame:
    frame_index: int
    timestamp_ms: int
    side: str
    phase: str

    com_velocity_x: float
    com_acceleration_x: float
    foot_x: float
    com_x: float
    shin_angle_deg: float | None

    contact_probability: float
    toe_off_probability: float | None
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class ContactPhaseMetrics:
    side: str
    phase: str
    frames_used: int

    braking_duration_ms: float | None
    propulsive_duration_ms: float | None
    braking_acceleration_area: float | None
    propulsive_acceleration_area: float | None
    braking_index: float | None
    propulsion_effectiveness_score: float | None
    net_horizontal_propulsion_score: float | None
    contact_direction_quality: str
    confidence: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
