from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class FootContactEvent:
    side: str
    frame_index: int
    timestamp_ms: int

    foot_x: float
    foot_y: float
    com_x: float
    com_y: float

    toe_x: float | None
    toe_y: float | None
    heel_x: float | None
    heel_y: float | None

    confidence: float

    leg_split: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class StrideGeometryContext:
    body_height_normalized: float | None = None
    leg_length_normalized: float | None = None
    real_world_scale_m_per_unit: float | None = None
    athlete_height_m: float | None = None


@dataclass(slots=True, frozen=True)
class StrideGeometryMetrics:
    contacts_used: int

    left_step_length_normalized: float | None
    right_step_length_normalized: float | None
    average_step_length_normalized: float | None
    average_stride_length_normalized: float | None

    average_step_length_m: float | None
    average_stride_length_m: float | None

    normalized_step_length_leg_ratio: float | None
    expected_optimal_step_length_normalized: float | None
    optimal_step_length_difference_percent: float | None

    average_step_width_normalized: float | None
    average_step_width_m: float | None

    average_foot_offset_from_com_percent_body_height: float | None
    crossover_contacts: int
    crossover_rate_percent: float | None

    toe_in_contacts: int
    neutral_toe_contacts: int
    toe_out_contacts: int

    step_length_symmetry_score: float | None
    geometry_stability_score: float | None
    overall_stride_geometry_score: float | None

    rating: str
    confidence: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
