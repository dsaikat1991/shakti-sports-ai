from __future__ import annotations

from app.services.readiness.components import (
    build_coach_issue_component,
    build_measurement_confidence,
    build_movement_consistency,
    build_physical_readiness,
    build_technical_readiness,
)
from app.services.readiness.flags import (
    build_readiness_flags,
)
from app.services.readiness.models import (
    CompetitionReadinessResult,
    ReadinessComponent,
)
from app.services.readiness.scoring import (
    geometric_confidence,
    readiness_status,
    weighted_mean,
)


def _overall_score(
    components: tuple[
        ReadinessComponent,
        ...
    ],
) -> float | None:
    return weighted_mean(
        [
            (
                component.score,
                component.weight,
            )
            for component in components
        ]
    )


def _summary(
    *,
    status: str,
    components: tuple[
        ReadinessComponent,
        ...
    ],
) -> str:
    available = [
        component
        for component in components
        if component.score is not None
    ]

    if not available:
        return (
            "Competition readiness could not be estimated "
            "from the available evidence."
        )

    weakest = min(
        available,
        key=lambda component: (
            component.score
        ),
    )

    strongest = max(
        available,
        key=lambda component: (
            component.score
        ),
    )

    return (
        f"Status: {status.replace('_', ' ')}. "
        f"Strongest component: "
        f"{strongest.name.replace('_', ' ')}. "
        f"Main attention area: "
        f"{weakest.name.replace('_', ' ')}."
    )


def analyze_competition_readiness(
    *,
    inputs: dict,
) -> dict:
    technical = build_technical_readiness(
        mechanical_efficiency_score=inputs.get(
            "mechanical_efficiency_score"
        ),
        force_application_score=inputs.get(
            "force_application_score"
        ),
        front_side_score=inputs.get(
            "front_side_score"
        ),
        back_side_score=inputs.get(
            "back_side_score"
        ),
        stability_pillar_score=inputs.get(
            "stability_pillar_score"
        ),
        confidences=inputs.get(
            "technical_confidences",
            [],
        ),
    )

    physical = build_physical_readiness(
        fatigue_pattern_detected=inputs.get(
            "fatigue_pattern_detected"
        ),
        fatigue_evidence_count=inputs.get(
            "fatigue_evidence_count"
        ),
        recent_efficiency_change_percent=inputs.get(
            "recent_efficiency_change_percent"
        ),
        recent_ground_contact_change_percent=inputs.get(
            "recent_ground_contact_change_percent"
        ),
        recent_cadence_change_percent=inputs.get(
            "recent_cadence_change_percent"
        ),
        confidences=inputs.get(
            "physical_confidences",
            [],
        ),
    )

    consistency = build_movement_consistency(
        mechanical_efficiency_cv=inputs.get(
            "mechanical_efficiency_cv"
        ),
        cadence_cv_percent=inputs.get(
            "cadence_cv_percent"
        ),
        contact_cv_percent=inputs.get(
            "contact_cv_percent"
        ),
        symmetry_score=inputs.get(
            "symmetry_score"
        ),
        confidences=inputs.get(
            "consistency_confidences",
            [],
        ),
    )

    coach_load = build_coach_issue_component(
        critical_issues=int(
            inputs.get(
                "critical_issues",
                0,
            )
        ),
        high_issues=int(
            inputs.get(
                "high_issues",
                0,
            )
        ),
        medium_issues=int(
            inputs.get(
                "medium_issues",
                0,
            )
        ),
        confidences=inputs.get(
            "coach_confidences",
            [],
        ),
    )

    measurement = build_measurement_confidence(
        recording_quality_score=inputs.get(
            "recording_quality_score"
        ),
        analysis_confidence_percent=inputs.get(
            "analysis_confidence_percent"
        ),
        valid_frame_percent=inputs.get(
            "valid_frame_percent"
        ),
    )

    components = (
        technical,
        physical,
        consistency,
        coach_load,
        measurement,
    )

    score = _overall_score(
        components
    )

    status = readiness_status(
        score
    )

    overall_confidence = (
        geometric_confidence(
            [
                component.confidence
                for component in components
                if component.score is not None
            ]
        )
    )

    flags = build_readiness_flags(
        personal_best_detected=bool(
            inputs.get(
                "personal_best_detected",
                False,
            )
        ),
        plateau_detected=bool(
            inputs.get(
                "plateau_detected",
                False,
            )
        ),
        fatigue_pattern_detected=bool(
            inputs.get(
                "fatigue_pattern_detected",
                False,
            )
        ),
        technique_regression_detected=bool(
            inputs.get(
                "technique_regression_detected",
                False,
            )
        ),
        mechanical_breakthrough_detected=bool(
            inputs.get(
                "mechanical_breakthrough_detected",
                False,
            )
        ),
        measurement_confidence_score=(
            measurement.score
        ),
    )

    result = CompetitionReadinessResult(
        score=score,
        status=status,
        confidence=(
            round(
                overall_confidence
                * 100.0,
                2,
            )
            if overall_confidence
            is not None
            else None
        ),
        components=components,
        flags=flags,
        summary=_summary(
            status=status,
            components=components,
        ),
        validation_level="experimental",
        engine_version="1.0.0",
        limitations=(
            "This is a deterministic readiness estimate, not a medical clearance.",
            "The engine does not currently use sleep, illness, soreness, training-load, or psychological-readiness data.",
            "Readiness should be reviewed with a qualified coach and, where relevant, medical staff.",
            "Thresholds and weights require prospective validation against competition outcomes.",
        ),
    )

    return {
        "status": (
            "experimental"
            if score is not None
            else "insufficient_data"
        ),
        "competition_readiness": (
            result.to_dict()
        ),
    }
