from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.athlete_intelligence.models import (
    AthleteSessionProfile,
)
from app.services.athlete_intelligence.scoring import (
    coefficient_of_variation_percent,
    weighted_score,
)


DEFAULT_CONSISTENCY_FEATURES = (
    "mechanical_efficiency_score",
    "ground_contact_ms",
    "cadence_spm",
    "symmetry_score",
    "sprint_economy_score",
)


def analyze_consistency(
    sessions: list[AthleteSessionProfile],
    *,
    feature_names: tuple[str, ...] = DEFAULT_CONSISTENCY_FEATURES,
) -> dict[str, Any]:
    if len(sessions) < 3:
        return {
            "status": "insufficient_data",
        }

    feature_results = {}
    score_components = []

    for feature_name in feature_names:
        values = [
            session.features[
                feature_name
            ]
            for session in sessions
            if feature_name
            in session.features
        ]

        if len(values) < 3:
            continue

        cv = coefficient_of_variation_percent(
            values
        )

        consistency_score = (
            None
            if cv is None
            else round(
                max(
                    0.0,
                    100.0
                    - cv * 5.0,
                ),
                2,
            )
        )

        feature_results[
            feature_name
        ] = {
            "samples": len(values),
            "average": round(
                mean(values),
                4,
            ),
            "coefficient_of_variation_percent": (
                round(
                    cv,
                    2,
                )
                if cv is not None
                else None
            ),
            "consistency_score": (
                consistency_score
            ),
        }

        score_components.append(
            (
                consistency_score,
                1.0,
            )
        )

    overall = weighted_score(
        score_components
    )

    return {
        "status": (
            "completed"
            if overall is not None
            else "insufficient_data"
        ),
        "overall_consistency_score": overall,
        "classification": (
            "high"
            if overall is not None
            and overall >= 85.0
            else "moderate"
            if overall is not None
            and overall >= 70.0
            else "low"
            if overall is not None
            else "insufficient_data"
        ),
        "features": feature_results,
        "engine_version": "0.1.0",
    }
