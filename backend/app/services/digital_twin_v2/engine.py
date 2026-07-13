from __future__ import annotations

from typing import Any

from app.services.digital_twin_v2.adaptation import (
    detect_adaptations,
)
from app.services.digital_twin_v2.baseline import (
    build_personal_baselines,
)
from app.services.digital_twin_v2.deviation import (
    compare_current_to_baseline,
)
from app.services.digital_twin_v2.fatigue import (
    detect_personal_fatigue_signature,
)
from app.services.digital_twin_v2.identity import (
    build_personal_identity_vector,
)
from app.services.digital_twin_v2.intervention import (
    evaluate_intervention_response,
)
from app.services.digital_twin_v2.models import (
    TwinSession,
    TwinState,
)
from app.services.digital_twin_v2.readiness import (
    build_personal_readiness_summary,
)
from app.services.digital_twin_v2.regression import (
    detect_regressions,
)
from app.services.digital_twin_v2.statistics import (
    confidence_percent,
)
from app.services.digital_twin_v2.trends import (
    analyze_longitudinal_trends,
)


def build_individual_digital_twin(
    sessions: list[TwinSession],
) -> dict[str, Any]:
    if len(sessions) < 3:
        return {
            "status": "insufficient_data",
        }

    ordered = sorted(
        sessions,
        key=lambda item: item.recorded_at,
    )

    latest = ordered[-1]

    baseline_sessions = (
        ordered[:-1]
        if len(ordered) > 3
        else ordered
    )

    baselines = build_personal_baselines(
        baseline_sessions,
    )

    deviations = compare_current_to_baseline(
        latest=latest,
        baselines=baselines,
    )

    trends = analyze_longitudinal_trends(
        ordered
    )

    adaptations = detect_adaptations(
        trends,
        deviations,
    )

    regressions = detect_regressions(
        trends,
        deviations,
    )

    fatigue = detect_personal_fatigue_signature(
        ordered
    )

    interventions = (
        evaluate_intervention_response(
            ordered
        )
    )

    identity = build_personal_identity_vector(
        ordered
    )

    readiness = (
        build_personal_readiness_summary(
            deviations=deviations,
            fatigue_signature=fatigue,
            regressions=regressions,
            adaptations=adaptations,
        )
    )

    confidence_values = [
        value
        for session in ordered
        if session.confidences
        for value in session.confidences.values()
    ]

    twin = TwinState(
        athlete_id=latest.athlete_id,
        event=latest.event,
        sessions_analyzed=len(
            ordered
        ),
        latest_performance_id=(
            latest.performance_id
        ),
        latest_recorded_at=(
            latest.recorded_at
        ),
        baselines=baselines,
        current_deviations=deviations,
        trends=trends,
        adaptations=adaptations,
        regressions=regressions,
        fatigue_signature=fatigue,
        intervention_response=(
            interventions
        ),
        readiness=readiness,
        identity_vector=identity.get(
            "vector",
            {},
        ),
        confidence=confidence_percent(
            confidence_values
        ),
    )

    return {
        "status": "experimental",
        "digital_twin": twin.to_dict(),
        "validation_level": "experimental",
        "engine_version": "1.0.0",
        "limitations": [
            "The twin models measured session history and does not simulate physiology.",
            "The model is only as reliable as the consistency and quality of uploaded recordings.",
            "Changes should be interpreted with qualified coaching context.",
        ],
    }
