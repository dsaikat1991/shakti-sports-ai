from __future__ import annotations

from app.services.sprint.mechanical_efficiency_models import (
    MechanicalEfficiencyResult,
    PillarScore,
)
from app.services.sprint.mechanical_efficiency_pillars import (
    build_back_side_pillar,
    build_force_application_pillar,
    build_front_side_pillar,
    build_rhythm_pillar,
    build_stability_pillar,
)
from app.services.sprint.mechanical_efficiency_scoring import (
    confidence_to_percent,
    geometric_confidence,
    rating_for_score,
)


def _weighted_pillar_score(
    pillars: tuple[PillarScore, ...],
) -> float | None:
    available = [
        pillar
        for pillar in pillars
        if pillar.score is not None
    ]

    if not available:
        return None

    total_weight = sum(
        pillar.weight
        for pillar in available
    )

    if total_weight <= 0:
        return None

    return round(
        sum(
            pillar.score
            * pillar.weight
            for pillar in available
        )
        / total_weight,
        2,
    )


def analyze_mechanical_efficiency(
    *,
    inputs: dict,
) -> dict:
    force = build_force_application_pillar(
        ground_contact_ms=inputs.get(
            "ground_contact_ms"
        ),
        push_off_completion_score=inputs.get(
            "push_off_completion_score"
        ),
        hip_extension_deg=inputs.get(
            "hip_extension_deg"
        ),
        com_acceleration_score=inputs.get(
            "com_acceleration_score"
        ),
        shin_angle_deg=inputs.get(
            "shin_angle_deg"
        ),
        confidence_values=inputs.get(
            "force_confidences",
            [],
        ),
    )

    rhythm = build_rhythm_pillar(
        cadence_spm=inputs.get(
            "cadence_spm"
        ),
        cadence_cv_percent=inputs.get(
            "cadence_cv_percent"
        ),
        contact_cv_percent=inputs.get(
            "contact_cv_percent"
        ),
        flight_cv_percent=inputs.get(
            "flight_cv_percent"
        ),
        cycle_consistency_score=inputs.get(
            "cycle_consistency_score"
        ),
        confidence_values=inputs.get(
            "rhythm_confidences",
            [],
        ),
    )

    front_side = build_front_side_pillar(
        front_side_score=inputs.get(
            "front_side_score"
        ),
        knee_lift_percent=inputs.get(
            "knee_lift_percent"
        ),
        recovery_velocity_dps=inputs.get(
            "recovery_velocity_dps"
        ),
        foot_offset_percent=inputs.get(
            "foot_offset_percent"
        ),
        confidence_values=inputs.get(
            "front_side_confidences",
            [],
        ),
    )

    back_side = build_back_side_pillar(
        back_side_score=inputs.get(
            "back_side_score"
        ),
        trailing_distance_percent=inputs.get(
            "trailing_distance_percent"
        ),
        heel_recovery_speed=inputs.get(
            "heel_recovery_speed"
        ),
        hip_extension_deg=inputs.get(
            "hip_extension_deg"
        ),
        back_side_duration_ms=inputs.get(
            "back_side_duration_ms"
        ),
        confidence_values=inputs.get(
            "back_side_confidences",
            [],
        ),
    )

    stability = build_stability_pillar(
        vertical_oscillation_percent=inputs.get(
            "vertical_oscillation_percent"
        ),
        pelvis_stability_score=inputs.get(
            "pelvis_stability_score"
        ),
        trunk_stability_score=inputs.get(
            "trunk_stability_score"
        ),
        symmetry_score=inputs.get(
            "symmetry_score"
        ),
        confidence_values=inputs.get(
            "stability_confidences",
            [],
        ),
    )

    pillars = (
        force,
        rhythm,
        front_side,
        back_side,
        stability,
    )

    score = _weighted_pillar_score(
        pillars
    )

    confidence = geometric_confidence(
        [
            pillar.confidence
            for pillar in pillars
            if pillar.score is not None
        ]
    )

    result = MechanicalEfficiencyResult(
        score=score,
        rating=rating_for_score(
            score
        ),
        confidence=confidence_to_percent(
            confidence
        ),
        pillars=pillars,
        validation_level="experimental",
        engine_version="0.1.0",
        limitations=(
            "Weights and thresholds are provisional.",
            "Inputs are primarily projected 2D or normalized estimates.",
            "The score is not yet validated against race performance or laboratory measurements.",
            "The score must not be used as a medical or injury-risk diagnosis.",
        ),
    )

    return {
        "status": (
            "experimental"
            if score is not None
            else "insufficient_data"
        ),
        "mechanical_efficiency": result.to_dict(),
    }
