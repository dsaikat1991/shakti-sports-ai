from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


SprintPhaseName = Literal[
    "standing",
    "start",
    "drive",
    "transition",
    "maximum_velocity",
    "deceleration",
]


@dataclass(slots=True, frozen=True)
class SprintSignalFrame:
    frame_index: int
    timestamp_ms: int
    com_position_x: float
    com_velocity_x: float
    com_acceleration_x: float
    torso_angle_deg: float | None = None
    cadence_spm: float | None = None
    ground_contact_ms: float | None = None
    flight_time_ms: float | None = None
    confidence: float = 1.0


@dataclass(slots=True, frozen=True)
class SprintPhaseFrame:
    frame_index: int
    timestamp_ms: int
    phase: SprintPhaseName
    confidence: float
    evidence: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class SprintPhaseSegment:
    phase: SprintPhaseName
    start_frame: int
    end_frame: int
    start_ms: int
    end_ms: int
    duration_ms: int
    average_confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
