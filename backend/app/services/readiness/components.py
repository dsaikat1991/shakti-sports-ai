from __future__ import annotations

from app.services.readiness.models import (
    ReadinessComponent,
)
from app.services.readiness.scoring import (
    clamp_score,
    geometric_confidence,
    inverse_risk_score,
    stability_score,
    weighted_mean,
)


def build_technical_readiness(
    *,
    mechanical_efficiency_score: float | None,
    force_application_score: float | None,
    front_side_score: float | None,
    back_side_score: float | None,
    stability_pillar_score: float | None,
    confidences: list[float | None],
) -> ReadinessComponent:
    score = weighted_mean(
        [
            (
                mechanical_efficiency_score,
                0.35,
            ),
            (
                force_application_score,
                0.20,
            ),
            (
                front_side_score,
                0.15,
            ),
            (
                back_side_score,
                0.15,
            ),
            (
                stability_pillar_score,
                0.15,
            ),
        ]
    )

    evidence: list[str] = []
    warnings: list[str] = []

    if (
        mechanical_efficiency_score
        is not None
    ):
        if mechanical_efficiency_score >= 85.0:
            evidence.append(
                "Mechanical efficiency is strong."
            )
        elif mechanical_efficiency_score < 70.0:
            warnings.append(
                "Mechanical efficiency is below the preferred competition range."
            )

    if (
        force_application_score
        is not None
        and force_application_score < 65.0
    ):
        warnings.append(
            "Force application requires attention."
        )

    return ReadinessComponent(
        name="technical_readiness",
        score=score,
        weight=0.30,
        confidence=geometric_confidence(
            confidences
        ),
        evidence=tuple(evidence),
        warnings=tuple(warnings),
    )


def build_physical_readiness(
    *,
    fatigue_pattern_detected: bool | None,
    fatigue_evidence_count: int | None,
    recent_efficiency_change_percent: float | None,
    recent_ground_contact_change_percent: float | None,
    recent_cadence_change_percent: float | None,
    confidences: list[float | None],
) -> ReadinessComponent:
    fatigue_penalty = 0.0

    if fatigue_pattern_detected:
        fatigue_penalty += 25.0

    if (
        fatigue_evidence_count
        is not None
    ):
        fatigue_penalty += min(
            20.0,
            max(
                0.0,
                float(
                    fatigue_evidence_count
                    - 1
                )
                * 5.0,
            ),
        )

    trend_adjustment = 0.0

    if (
        recent_efficiency_change_percent
        is not None
    ):
        trend_adjustment += max(
            -12.0,
            min(
                12.0,
                recent_efficiency_change_percent,
            ),
        )

    if (
        recent_ground_contact_change_percent
        is not None
    ):
        trend_adjustment += max(
            -10.0,
            min(
                10.0,
                -recent_ground_contact_change_percent,
            ),
        )

    if (
        recent_cadence_change_percent
        is not None
    ):
        trend_adjustment += max(
            -8.0,
            min(
                8.0,
                recent_cadence_change_percent,
            ),
        )

    score = clamp_score(
        85.0
        - fatigue_penalty
        + trend_adjustment
    )

    evidence: list[str] = []
    warnings: list[str] = []

    if fatigue_pattern_detected:
        warnings.append(
            "A recent multi-metric fatigue pattern was detected."
        )
    else:
        evidence.append(
            "No longitudinal fatigue pattern was detected."
        )

    if (
        recent_efficiency_change_percent
        is not None
        and recent_efficiency_change_percent > 2.0
    ):
        evidence.append(
            "Recent mechanical-efficiency trend is positive."
        )

    return ReadinessComponent(
        name="physical_readiness",
        score=score,
        weight=0.25,
        confidence=geometric_confidence(
            confidences
        ),
        evidence=tuple(evidence),
        warnings=tuple(warnings),
    )


def build_movement_consistency(
    *,
    mechanical_efficiency_cv: float | None,
    cadence_cv_percent: float | None,
    contact_cv_percent: float | None,
    symmetry_score: float | None,
    confidences: list[float | None],
) -> ReadinessComponent:
    consistency = stability_score(
        mechanical_efficiency_cv=(
            mechanical_efficiency_cv
        ),
        cadence_cv=(
            cadence_cv_percent
        ),
        contact_cv=(
            contact_cv_percent
        ),
    )

    score = weighted_mean(
        [
            (
                consistency,
                0.70,
            ),
            (
                symmetry_score,
                0.30,
            ),
        ]
    )

    evidence: list[str] = []
    warnings: list[str] = []

    if (
        consistency is not None
        and consistency >= 80.0
    ):
        evidence.append(
            "Recent movement metrics are consistent."
        )
    elif (
        consistency is not None
        and consistency < 65.0
    ):
        warnings.append(
            "Recent movement metrics show high variability."
        )

    if (
        symmetry_score is not None
        and symmetry_score < 75.0
    ):
        warnings.append(
            "Left-right symmetry is below the preferred competition range."
        )

    return ReadinessComponent(
        name="movement_consistency",
        score=score,
        weight=0.20,
        confidence=geometric_confidence(
            confidences
        ),
        evidence=tuple(evidence),
        warnings=tuple(warnings),
    )


def build_coach_issue_component(
    *,
    critical_issues: int,
    high_issues: int,
    medium_issues: int,
    confidences: list[float | None],
) -> ReadinessComponent:
    penalty = (
        critical_issues * 25.0
        + high_issues * 12.0
        + medium_issues * 5.0
    )

    score = clamp_score(
        100.0 - penalty
    )

    warnings: list[str] = []
    evidence: list[str] = []

    if critical_issues > 0:
        warnings.append(
            "Critical coaching issues are active."
        )
    elif high_issues > 0:
        warnings.append(
            "High-priority coaching issues are active."
        )
    else:
        evidence.append(
            "No critical coaching issue was detected."
        )

    return ReadinessComponent(
        name="coach_issue_load",
        score=score,
        weight=0.15,
        confidence=geometric_confidence(
            confidences
        ),
        evidence=tuple(evidence),
        warnings=tuple(warnings),
    )


def build_measurement_confidence(
    *,
    recording_quality_score: float | None,
    analysis_confidence_percent: float | None,
    valid_frame_percent: float | None,
) -> ReadinessComponent:
    score = weighted_mean(
        [
            (
                recording_quality_score,
                0.35,
            ),
            (
                analysis_confidence_percent,
                0.40,
            ),
            (
                valid_frame_percent,
                0.25,
            ),
        ]
    )

    confidence_values = [
        (
            recording_quality_score
            / 100.0
            if recording_quality_score
            is not None
            else None
        ),
        (
            analysis_confidence_percent
            / 100.0
            if analysis_confidence_percent
            is not None
            else None
        ),
        (
            valid_frame_percent
            / 100.0
            if valid_frame_percent
            is not None
            else None
        ),
    ]

    warnings: list[str] = []
    evidence: list[str] = []

    if score is not None and score >= 85.0:
        evidence.append(
            "Measurement confidence is high."
        )
    elif score is not None and score < 70.0:
        warnings.append(
            "Measurement quality limits readiness confidence."
        )

    return ReadinessComponent(
        name="measurement_confidence",
        score=score,
        weight=0.10,
        confidence=geometric_confidence(
            confidence_values
        ),
        evidence=tuple(evidence),
        warnings=tuple(warnings),
    )
