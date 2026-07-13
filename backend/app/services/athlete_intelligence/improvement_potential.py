from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.athlete_intelligence.models import (
    AthleteSessionProfile,
)
from app.services.athlete_intelligence.scoring import (
    LOWER_IS_BETTER,
    trend_slope,
    weighted_score,
)


def analyze_improvement_potential(
    sessions: list[AthleteSessionProfile],
    *,
    benchmark_percentiles: dict[str, float],
) -> dict[str, Any]:
    if len(sessions) < 3:
        return {
            "status": "insufficient_data",
        }

    opportunities = []

    feature_names = sorted(
        {
            feature_name
            for session in sessions
            for feature_name
            in session.features
        }
    )

    for feature_name in feature_names:
        values = [
            session.features[
                feature_name
            ]
            for session in sorted(
                sessions,
                key=lambda item: item.recorded_at,
            )
            if feature_name
            in session.features
        ]

        if len(values) < 3:
            continue

        slope = trend_slope(
            values
        )

        percentile = benchmark_percentiles.get(
            feature_name
        )

        if percentile is None:
            continue

        lower_is_better = (
            feature_name
            in LOWER_IS_BETTER
        )

        improvement_direction_positive = (
            slope < 0.0
            if lower_is_better
            else slope > 0.0
        )

        headroom = max(
            0.0,
            100.0
            - percentile,
        )

        momentum = min(
            100.0,
            abs(
                float(slope)
            )
            / max(
                abs(
                    mean(values)
                ),
                1e-9,
            )
            * 1000.0,
        )

        potential_score = weighted_score(
            [
                (
                    headroom,
                    0.65,
                ),
                (
                    momentum
                    if improvement_direction_positive
                    else 0.0,
                    0.35,
                ),
            ]
        )

        opportunities.append(
            {
                "feature_name": feature_name,
                "current_percentile": (
                    percentile
                ),
                "headroom_score": round(
                    headroom,
                    2,
                ),
                "trend_slope_per_session": (
                    round(
                        slope,
                        6,
                    )
                    if slope is not None
                    else None
                ),
                "positive_momentum": (
                    improvement_direction_positive
                ),
                "improvement_potential_score": (
                    potential_score
                ),
            }
        )

    opportunities.sort(
        key=lambda item: (
            item[
                "improvement_potential_score"
            ]
            or 0.0
        ),
        reverse=True,
    )

    overall = weighted_score(
        [
            (
                item[
                    "improvement_potential_score"
                ],
                1.0,
            )
            for item
            in opportunities[
                :5
            ]
        ]
    )

    return {
        "status": (
            "completed"
            if opportunities
            else "insufficient_data"
        ),
        "overall_improvement_potential_score": (
            overall
        ),
        "top_opportunities": opportunities[
            :5
        ],
        "engine_version": "0.1.0",
        "validation_level": "experimental",
        "limitations": [
            "Improvement potential reflects measured headroom and recent trend, not biological ceiling.",
            "The output is not a prediction of future competition performance.",
        ],
    }
