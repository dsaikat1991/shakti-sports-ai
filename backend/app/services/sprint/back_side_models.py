from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class BackSideFrame:
    frame_index: int
    timestamp_ms: int
    phase: str
    side: str

    shoulder_x: float
    shoulder_y: float
    hip_x: float
    hip_y: float
    knee_x: float
    knee_y: float
    ankle_x: float
    ankle_y: float
    heel_x: float
    heel_y: float
    toe_x: float
    toe_y: float

    com_x: float
    com_y: float

    hip_angle_deg: float | None
    knee_angle_deg: float | None

    heel_velocity_x: float | None
    heel_velocity_y: float | None
    ankle_velocity_x: float | None
    ankle_velocity_y: float | None

    toe_off_probability: float | None
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class BackSideMetrics:
    side: str
    phase: str
    frames_used: int

    maximum_hip_extension_deg: float | None
    maximum_trailing_foot_distance_body_height_percent: float | None
    peak_heel_recovery_speed_normalized: float | None
    average_back_side_duration_ms: float | None
    push_off_completion_score: float | None
    rear_swing_velocity_normalized: float | None

    back_side_risk: str
    score: float | None
    confidence: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
