from __future__ import annotations

from typing import Any

from app.services.athlete_intelligence.scoring import (
    weighted_score,
)


def calculate_trainability_index(
    *,
    consistency_score: float | None,
    improvement_potential_score: float | None,
    coach_rule_response_score: float | None,
    session_adherence_score: float | None,
    fatigue_resilience_score: float | None,
    measurement_confidence_score: float | None,
) -> dict[str, Any]:
    score = weighted_score(
        [
            (
                improvement_potential_score,
                0.30,
            ),
            (
                consistency_score,
                0.20,
            ),
            (
                coach_rule_response_score,
                0.20,
            ),
            (
                session_adherence_score,
                0.15,
            ),
            (
                fatigue_resilience_score,
                0.10,
            ),
            (
                measurement_confidence_score,
                0.05,
            ),
        ]
    )

    return {
        "status": (
            "experimental"
            if score is not None
            else "insufficient_data"
        ),
        "trainability_index": score,
        "classification": (
            "very_high"
            if score is not None
            and score >= 85.0
            else "high"
            if score is not None
            and score >= 75.0
            else "moderate"
            if score is not None
            and score >= 60.0
            else "low"
            if score is not None
            else "insufficient_data"
        ),
        "components": {
            "consistency_score": (
                consistency_score
            ),
            "improvement_potential_score": (
                improvement_potential_score
            ),
            "coach_rule_response_score": (
                coach_rule_response_score
            ),
            "session_adherence_score": (
                session_adherence_score
            ),
            "fatigue_resilience_score": (
                fatigue_resilience_score
            ),
            "measurement_confidence_score": (
                measurement_confidence_score
            ),
        },
        "engine_version": "0.1.0",
        "validation_level": "experimental",
        "limitations": [
            "Trainability is a behavioural and longitudinal index, not a genetic or biological determination.",
            "The index should not be used to exclude athletes from opportunities.",
        ],
    }
