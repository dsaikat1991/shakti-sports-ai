from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.athlete_intelligence.consistency import (
    analyze_consistency,
)
from app.services.athlete_intelligence.fatigue import (
    detect_fatigue_signature,
)
from app.services.athlete_intelligence.fingerprint import (
    build_biomechanical_fingerprint,
)
from app.services.athlete_intelligence.improvement_potential import (
    analyze_improvement_potential,
)
from app.services.athlete_intelligence.models import (
    AthleteSessionProfile,
)
from app.services.athlete_intelligence.strength_profile import (
    build_strength_profile,
)
from app.services.athlete_intelligence.trainability import (
    calculate_trainability_index,
)
from app.services.athlete_intelligence.weakness_profile import (
    build_weakness_profile,
)


def analyze_athlete_intelligence(
    *,
    sessions: list[AthleteSessionProfile],
    benchmark_percentiles: dict[str, float],
    coach_rule_response_score: float | None = None,
    session_adherence_score: float | None = None,
    measurement_confidence_score: float | None = None,
) -> dict[str, Any]:
    if not sessions:
        return {
            "status": "insufficient_data",
        }

    ordered = sorted(
        sessions,
        key=lambda item: item.recorded_at,
    )

    latest = ordered[-1]

    strengths = build_strength_profile(
        features=latest.features,
        percentiles=benchmark_percentiles,
        confidences=latest.confidences,
    )

    weaknesses = build_weakness_profile(
        features=latest.features,
        percentiles=benchmark_percentiles,
        confidences=latest.confidences,
    )

    fingerprint = (
        build_biomechanical_fingerprint(
            ordered
        )
    )

    consistency = analyze_consistency(
        ordered
    )

    fatigue = detect_fatigue_signature(
        ordered
    )

    improvement = (
        analyze_improvement_potential(
            ordered,
            benchmark_percentiles=(
                benchmark_percentiles
            ),
        )
    )

    fatigue_resilience_score = (
        100.0
        - fatigue.get(
            "fatigue_signature_score",
            0.0,
        )
        if fatigue.get(
            "status"
        )
        == "completed"
        else None
    )

    trainability = calculate_trainability_index(
        consistency_score=(
            consistency.get(
                "overall_consistency_score"
            )
        ),
        improvement_potential_score=(
            improvement.get(
                "overall_improvement_potential_score"
            )
        ),
        coach_rule_response_score=(
            coach_rule_response_score
        ),
        session_adherence_score=(
            session_adherence_score
        ),
        fatigue_resilience_score=(
            fatigue_resilience_score
        ),
        measurement_confidence_score=(
            measurement_confidence_score
        ),
    )

    top_scores = [
        value
        for value in (
            consistency.get(
                "overall_consistency_score"
            ),
            improvement.get(
                "overall_improvement_potential_score"
            ),
            trainability.get(
                "trainability_index"
            ),
        )
        if isinstance(
            value,
            (int, float),
        )
    ]

    overall = (
        round(
            mean(
                top_scores
            ),
            2,
        )
        if top_scores
        else None
    )

    return {
        "status": "experimental",
        "athlete_id": latest.athlete_id,
        "event": latest.event,
        "sessions_analyzed": len(
            ordered
        ),
        "overall_athlete_intelligence_score": (
            overall
        ),
        "strength_profile": strengths,
        "weakness_profile": weaknesses,
        "biomechanical_fingerprint": (
            fingerprint
        ),
        "consistency": consistency,
        "fatigue_signature": fatigue,
        "improvement_potential": (
            improvement
        ),
        "trainability": trainability,
        "engine_version": "0.1.0",
        "validation_level": "experimental",
        "limitations": [
            "This engine summarizes measured performance patterns and does not determine innate talent.",
            "Outputs should support, not replace, qualified coaching and scouting judgment.",
            "No athlete should be excluded solely because of these scores.",
        ],
    }
