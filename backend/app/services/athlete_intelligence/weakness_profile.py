from __future__ import annotations

from typing import Any

from app.services.athlete_intelligence.models import (
    RankedFeature,
)
from app.services.athlete_intelligence.strength_profile import (
    FEATURE_CATEGORIES,
)


def build_weakness_profile(
    *,
    features: dict[str, float],
    percentiles: dict[str, float],
    confidences: dict[str, float] | None = None,
    maximum_percentile: float = 35.0,
    maximum_items: int = 6,
) -> dict[str, Any]:
    active_confidences = confidences or {}

    weaknesses: list[RankedFeature] = []

    for feature_name, percentile in percentiles.items():
        if feature_name not in features:
            continue

        if percentile > maximum_percentile:
            continue

        priority_score = round(
            100.0 - percentile,
            2,
        )

        explanation = (
            f"{feature_name} is at the "
            f"{round(percentile, 1)}th percentile "
            "and is a candidate development area."
        )

        weaknesses.append(
            RankedFeature(
                feature_name=feature_name,
                value=float(
                    features[
                        feature_name
                    ]
                ),
                score=priority_score,
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

    weaknesses.sort(
        key=lambda item: item.score,
        reverse=True,
    )

    selected = weaknesses[
        :maximum_items
    ]

    return {
        "status": (
            "completed"
            if selected
            else "insufficient_evidence"
        ),
        "weaknesses": [
            item.to_dict()
            for item in selected
        ],
        "priority_categories": list(
            dict.fromkeys(
                item.category
                for item in selected
            )
        ),
        "engine_version": "0.1.0",
    }
