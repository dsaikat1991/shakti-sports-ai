from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class GaitDetectorConfig:
    contact_threshold: float = 0.66
    toe_off_threshold: float = 0.60
    minimum_event_gap_ms: int = 70
    minimum_same_side_stride_ms: int = 220
    maximum_same_side_stride_ms: int = 1400
    alternation_bonus: float = 0.08
    same_side_penalty: float = 0.12
    local_peak_radius: int = 2
    confidence_floor: float = 0.50
