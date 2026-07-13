from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class FrontSideFrame:
    frame_index: int
    timestamp_ms: int
    phase: str
    side: str

    hip_x: float
    hip_y: float
    knee_x: float
    knee_y: float
    ankle_x: float
    ankle_y: float
    foot_x: float
    foot_y: float

    com_x: float
    com_y: float

    knee_angle_deg: float | None
    hip_angle_deg: float | None
    knee_angular_velocity_dps: float | None
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class FrontSideMetrics:
    side: str
    phase: str
    frames_used: int

    maximum_knee_lift_body_height_percent: float | None
    maximum_thigh_angle_deg: float | None
    peak_knee_recovery_velocity_dps: float | None
    average_foot_strike_offset_from_com_percent: float | None
    average_shin_angle_before_contact_deg: float | None
    overstride_risk: str
    score: float | None
    confidence: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
