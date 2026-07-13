from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any

@dataclass(slots=True, frozen=True)
class ScalarSample:
    frame_index: int
    timestamp_ms: int
    value: float
    confidence: float = 1.0

@dataclass(slots=True, frozen=True)
class ScalarMotionState:
    frame_index: int
    timestamp_ms: int
    value: float
    velocity: float
    acceleration: float
    jerk: float
    confidence: float
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(slots=True, frozen=True)
class PointSample:
    frame_index: int
    timestamp_ms: int
    x: float
    y: float
    confidence: float = 1.0

@dataclass(slots=True, frozen=True)
class PointMotionState:
    frame_index: int
    timestamp_ms: int
    x: float
    y: float
    velocity_x: float
    velocity_y: float
    speed: float
    acceleration_x: float
    acceleration_y: float
    acceleration_magnitude: float
    jerk_x: float
    jerk_y: float
    jerk_magnitude: float
    confidence: float
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(slots=True, frozen=True)
class SegmentDefinition:
    name: str
    proximal_keypoint: str
    distal_keypoint: str

@dataclass(slots=True, frozen=True)
class SegmentKinematicState:
    segment_name: str
    frame_index: int
    timestamp_ms: int
    midpoint_x: float
    midpoint_y: float
    length: float
    orientation_degrees: float
    linear_velocity_x: float
    linear_velocity_y: float
    linear_speed: float
    angular_velocity_dps: float
    confidence: float
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
