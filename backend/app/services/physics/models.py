from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class PhysicsSample:
    frame_index: int
    timestamp_ms: int
    com_x: float
    com_y: float
    velocity_x: float
    velocity_y: float
    acceleration_x: float
    acceleration_y: float
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class EnergyState:
    frame_index: int
    timestamp_ms: int
    normalized_kinetic_energy: float
    normalized_potential_energy: float
    normalized_mechanical_energy: float
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class ImpulseState:
    start_ms: int
    end_ms: int
    duration_ms: int
    normalized_horizontal_impulse: float
    normalized_vertical_impulse: float
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class PowerState:
    frame_index: int
    timestamp_ms: int
    normalized_horizontal_power: float
    normalized_vertical_power: float
    normalized_total_power: float
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
