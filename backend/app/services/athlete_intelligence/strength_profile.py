from __future__ import annotations

from typing import Any

from app.services.athlete_intelligence.models import (
    RankedFeature,
)
from app.services.athlete_intelligence.scoring import (
    LOWER_IS_BETTER,
)


FEATURE_CATEGORIES = {
    "mechanical_efficiency_score": "overall",
    "horizontal_force_score": "force",
    "net_propulsion_score": "force",
    "leg_spring_score": "elasticity",
    "stride_geometry_score": "geometry",
    "foot_trajectory_score": "recovery",
    "arm_mechanics_score": "coordination",
    "pelvis_trunk_score": "stability",
    "max_velocity_maintenance_score": "speed_endurance",
    "sprint_economy_score": "economy",
    "symmetry_score": "symmetry",
    "competition_readiness_score": "readiness",
}


def build_strength_profile(
    *,
    features: dict[str, float],
    percentiles: dict[str, float],
    confidences: dict[str, float] | None = None,
    minimum_percentile: float = 75.0,
    maximum_items: int = 6,
) -> dict[str, Any]:
    active_confidences = confidences or {}

    strengths: list[RankedFeature] = []

    for feature_name, percentile in percentiles.items():
        if feature_name not in features:
            continue

        if percentile < minimum_percentile:
            continue

        explanation = (
            f"{feature_name} is at the "
            f"{round(percentile, 1)}th percentile "
            "within the selected comparison cohort."
        )

        strengths.append(
            RankedFeature(
                feature_name=feature_name,
                value=float(
                    features[
                        feature_name
                    ]
                ),
                score=float(percentile),
                confidence=(
                    round(
                        active_confidences[
                            feature_name
                        ]
                        * 100.0,
                        2,
                    )
                    if feature_name
                    in active_confidences
                    else None
                ),
                category=FEATURE_CATEGORIES.get(
                    feature_name,
                    "other",
                ),
                explanation=explanation,
            )
        )

    strengths.sort(
        key=lambda item: item.score,
        reverse=True,
    )

    selected = strengths[
        :maximum_items
    ]

    return {
        "status": (
            "completed"
            if selected
            else "insufficient_evidence"
        ),
        "strengths": [
            item.to_dict()
            for item in selected
        ],
        "dominant_categories": list(
            dict.fromkeys(
                item.category
                for item in selected
            )
        ),
        "engine_version": "0.1.0",
    }
