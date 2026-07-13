from __future__ import annotations

from typing import Any

from app.services.sprint.mechanical_efficiency_models import (
    PillarScore,
)
from app.services.sprint.mechanical_efficiency_scoring import (
    geometric_confidence,
    score_inverse_range,
    score_target_range,
    weighted_mean,
)


def build_force_application_pillar(
    *,
    ground_contact_ms: float | None,
    push_off_completion_score: float | None,
    hip_extension_deg: float | None,
    com_acceleration_score: float | None,
    shin_angle_deg: float | None,
    confidence_values: list[float | None],
) -> PillarScore:
    contact_score = score_inverse_range(
        ground_contact_ms,
        ideal_max=105.0,
        poor_max=180.0,
    )

    hip_score = score_target_range(
        hip_extension_deg,
        ideal_min=145.0,
        ideal_max=175.0,
        tolerance=35.0,
    )

    shin_score = score_target_range(
        shin_angle_deg,
        ideal_min=55.0,
        ideal_max=85.0,
        tolerance=35.0,
    )

    score = weighted_mean(
        [
            (contact_score, 0.25),
            (
                push_off_completion_score,
                0.25,
            ),
            (hip_score, 0.20),
            (
                com_acceleration_score,
                0.20,
            ),
            (shin_score, 0.10),
        ]
    )

    evidence: list[str] = []
    penalties: list[str] = []

    if push_off_completion_score is not None:
        if push_off_completion_score >= 80.0:
            evidence.append(
                "Strong push-off completion."
            )
        elif push_off_completion_score < 60.0:
            penalties.append(
                "Push-off completion is limited."
            )

    if ground_contact_ms is not None:
        if ground_contact_ms <= 110.0:
            evidence.append(
                "Ground-contact time is efficient."
            )
        elif ground_contact_ms > 145.0:
            penalties.append(
                "Ground-contact time is prolonged."
            )

    if hip_extension_deg is not None:
        if hip_extension_deg >= 145.0:
            evidence.append(
                "Hip extension supports force application."
            )
        elif hip_extension_deg < 130.0:
            penalties.append(
                "Hip extension is limited."
            )

    return PillarScore(
        name="force_application",
        score=score,
        weight=0.25,
        confidence=geometric_confidence(
            confidence_values
        ),
        evidence=tuple(evidence),
        penalties=tuple(penalties),
        validation_level="experimental",
    )


def build_rhythm_pillar(
    *,
    cadence_spm: float | None,
    cadence_cv_percent: float | None,
    contact_cv_percent: float | None,
    flight_cv_percent: float | None,
    cycle_consistency_score: float | None,
    confidence_values: list[float | None],
) -> PillarScore:
    cadence_score = score_target_range(
        cadence_spm,
        ideal_min=250.0,
        ideal_max=310.0,
        tolerance=70.0,
    )

    cadence_consistency = score_inverse_range(
        cadence_cv_percent,
        ideal_max=3.0,
        poor_max=15.0,
    )

    contact_consistency = score_inverse_range(
        contact_cv_percent,
        ideal_max=4.0,
        poor_max=18.0,
    )

    flight_consistency = score_inverse_range(
        flight_cv_percent,
        ideal_max=5.0,
        poor_max=20.0,
    )

    score = weighted_mean(
        [
            (cadence_score, 0.25),
            (
                cadence_consistency,
                0.20,
            ),
            (
                contact_consistency,
                0.20,
            ),
            (
                flight_consistency,
                0.15,
            ),
            (
                cycle_consistency_score,
                0.20,
            ),
        ]
    )

    evidence: list[str] = []
    penalties: list[str] = []

    if cadence_cv_percent is not None:
        if cadence_cv_percent <= 4.0:
            evidence.append(
                "Cadence is consistent across cycles."
            )
        elif cadence_cv_percent > 10.0:
            penalties.append(
                "Cadence varies substantially."
            )

    if contact_cv_percent is not None:
        if contact_cv_percent <= 5.0:
            evidence.append(
                "Contact timing is stable."
            )
        elif contact_cv_percent > 12.0:
            penalties.append(
                "Contact timing is inconsistent."
            )

    return PillarScore(
        name="rhythm",
        score=score,
        weight=0.20,
        confidence=geometric_confidence(
            confidence_values
        ),
        evidence=tuple(evidence),
        penalties=tuple(penalties),
        validation_level="experimental",
    )


def build_front_side_pillar(
    *,
    front_side_score: float | None,
    knee_lift_percent: float | None,
    recovery_velocity_dps: float | None,
    foot_offset_percent: float | None,
    confidence_values: list[float | None],
) -> PillarScore:
    knee_lift_score = score_target_range(
        knee_lift_percent,
        ideal_min=35.0,
        ideal_max=60.0,
        tolerance=30.0,
    )

    recovery_score = score_target_range(
        recovery_velocity_dps,
        ideal_min=550.0,
        ideal_max=1000.0,
        tolerance=500.0,
    )

    strike_score = score_target_range(
        abs(
            foot_offset_percent
        )
        if foot_offset_percent is not None
        else None,
        ideal_min=0.0,
        ideal_max=10.0,
        tolerance=30.0,
    )

    score = weighted_mean(
        [
            (front_side_score, 0.45),
            (knee_lift_score, 0.20),
            (recovery_score, 0.20),
            (strike_score, 0.15),
        ]
    )

    evidence: list[str] = []
    penalties: list[str] = []

    if knee_lift_percent is not None:
        if knee_lift_percent >= 35.0:
            evidence.append(
                "Knee lift supports front-side mechanics."
            )
        elif knee_lift_percent < 25.0:
            penalties.append(
                "Knee lift is limited."
            )

    if foot_offset_percent is not None:
        if abs(foot_offset_percent) <= 10.0:
            evidence.append(
                "Foot strike is close to the COM."
            )
        elif foot_offset_percent > 20.0:
            penalties.append(
                "Foot strike is substantially ahead of the COM."
            )

    return PillarScore(
        name="front_side_efficiency",
        score=score,
        weight=0.20,
        confidence=geometric_confidence(
            confidence_values
        ),
        evidence=tuple(evidence),
        penalties=tuple(penalties),
        validation_level="experimental",
    )


def build_back_side_pillar(
    *,
    back_side_score: float | None,
    trailing_distance_percent: float | None,
    heel_recovery_speed: float | None,
    hip_extension_deg: float | None,
    back_side_duration_ms: float | None,
    confidence_values: list[float | None],
) -> PillarScore:
    trailing_score = score_inverse_range(
        trailing_distance_percent,
        ideal_max=15.0,
        poor_max=45.0,
    )

    recovery_score = score_target_range(
        heel_recovery_speed,
        ideal_min=1.2,
        ideal_max=3.0,
        tolerance=1.5,
    )

    extension_score = score_target_range(
        hip_extension_deg,
        ideal_min=145.0,
        ideal_max=175.0,
        tolerance=35.0,
    )

    duration_score = score_inverse_range(
        back_side_duration_ms,
        ideal_max=150.0,
        poor_max=350.0,
    )

    score = weighted_mean(
        [
            (back_side_score, 0.40),
            (trailing_score, 0.20),
            (recovery_score, 0.15),
            (extension_score, 0.15),
            (duration_score, 0.10),
        ]
    )

    evidence: list[str] = []
    penalties: list[str] = []

    if trailing_distance_percent is not None:
        if trailing_distance_percent <= 15.0:
            evidence.append(
                "Trailing distance is well controlled."
            )
        elif trailing_distance_percent > 30.0:
            penalties.append(
                "Rear-leg trailing distance is excessive."
            )

    if back_side_duration_ms is not None:
        if back_side_duration_ms <= 160.0:
            evidence.append(
                "Back-side duration is efficient."
            )
        elif back_side_duration_ms > 260.0:
            penalties.append(
                "The leg remains behind the COM too long."
            )

    return PillarScore(
        name="back_side_efficiency",
        score=score,
        weight=0.20,
        confidence=geometric_confidence(
            confidence_values
        ),
        evidence=tuple(evidence),
        penalties=tuple(penalties),
        validation_level="experimental",
    )


def build_stability_pillar(
    *,
    vertical_oscillation_percent: float | None,
    pelvis_stability_score: float | None,
    trunk_stability_score: float | None,
    symmetry_score: float | None,
    confidence_values: list[float | None],
) -> PillarScore:
    oscillation_score = score_inverse_range(
        vertical_oscillation_percent,
        ideal_max=6.0,
        poor_max=16.0,
    )

    score = weighted_mean(
        [
            (oscillation_score, 0.30),
            (
                pelvis_stability_score,
                0.25,
            ),
            (
                trunk_stability_score,
                0.20,
            ),
            (symmetry_score, 0.25),
        ]
    )

    evidence: list[str] = []
    penalties: list[str] = []

    if vertical_oscillation_percent is not None:
        if vertical_oscillation_percent <= 7.0:
            evidence.append(
                "Vertical oscillation is controlled."
            )
        elif vertical_oscillation_percent > 12.0:
            penalties.append(
                "Vertical oscillation is excessive."
            )

    if symmetry_score is not None:
        if symmetry_score >= 90.0:
            evidence.append(
                "Left-right mechanics are highly symmetrical."
            )
        elif symmetry_score < 75.0:
            penalties.append(
                "Left-right asymmetry reduces stability."
            )

    return PillarScore(
        name="stability",
        score=score,
        weight=0.15,
        confidence=geometric_confidence(
            confidence_values
        ),
        evidence=tuple(evidence),
        penalties=tuple(penalties),
        validation_level="experimental",
    )
