from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class FeatureDefinition:
    name: str
    unit: str | None
    tier: str
    source_stage: str
    description: str
    required_context: tuple[str, ...] = ()
    version: str = "0.1.0"


DEFAULT_FEATURE_DEFINITIONS: dict[
    str,
    FeatureDefinition,
] = {
    "left_knee_max_flexion_deg": FeatureDefinition(
        name="left_knee_max_flexion_deg",
        unit="deg",
        tier="measured",
        source_stage="biomechanics",
        description="Maximum projected 2D left-knee flexion.",
    ),
    "right_knee_max_flexion_deg": FeatureDefinition(
        name="right_knee_max_flexion_deg",
        unit="deg",
        tier="measured",
        source_stage="biomechanics",
        description="Maximum projected 2D right-knee flexion.",
    ),
    "cadence_spm": FeatureDefinition(
        name="cadence_spm",
        unit="steps/min",
        tier="estimated",
        source_stage="gait",
        description="Estimated cadence from fused gait events.",
    ),
    "ground_contact_time_ms": FeatureDefinition(
        name="ground_contact_time_ms",
        unit="ms",
        tier="estimated",
        source_stage="gait",
        description="Estimated ground-contact duration.",
        required_context=("side",),
    ),
    "flight_time_ms": FeatureDefinition(
        name="flight_time_ms",
        unit="ms",
        tier="estimated",
        source_stage="gait",
        description="Estimated flight duration.",
    ),
    "vertical_oscillation_body_height_percent": FeatureDefinition(
        name="vertical_oscillation_body_height_percent",
        unit="percent",
        tier="estimated",
        source_stage="biomechanics",
        description="Pose-derived vertical oscillation relative to body height.",
    ),
    "stride_symmetry_score": FeatureDefinition(
        name="stride_symmetry_score",
        unit="score_0_100",
        tier="estimated",
        source_stage="biomechanics",
        description="Left-right stride symmetry score.",
    ),
    "peak_normalized_horizontal_power": FeatureDefinition(
        name="peak_normalized_horizontal_power",
        unit="normalized",
        tier="estimated",
        source_stage="physics",
        description="Mass-normalized camera-relative horizontal power proxy.",
    ),
    "sprint_phase_confidence": FeatureDefinition(
        name="sprint_phase_confidence",
        unit="percent",
        tier="estimated",
        source_stage="athletics",
        description="Confidence assigned to an automatically detected sprint phase.",
        required_context=("phase",),
    ),
}
