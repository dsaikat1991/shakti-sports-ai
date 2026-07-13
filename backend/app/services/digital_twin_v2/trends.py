from __future__ import annotations

from typing import Any

from app.services.digital_twin_v2.models import (
    TwinSession,
)
from app.services.digital_twin_v2.statistics import (
    coefficient_of_variation_percent,
    performance_direction,
    slope,
)


def analyze_longitudinal_trends(
    sessions: list[TwinSession],
    *,
    minimum_samples: int = 3,
) -> dict[str, Any]:
    ordered = sorted(
        sessions,
        key=lambda item: item.recorded_at,
    )

    feature_names = sorted(
        {
            feature_name
            for session in ordered
            for feature_name
            in session.features
        }
    )

    trends = {}

    for feature_name in feature_names:
        values = [
            float(
                session.features[
                    feature_name
                ]
            )
            for session in ordered
            if feature_name
            in session.features
        ]

        if len(values) < minimum_samples:
            continue

        slope_value = slope(
            values
        )

        average = sum(values) / len(values)

        practical_threshold = max(
            abs(average)
            * 0.0025,
            1e-9,
        )

        direction = performance_direction(
            feature_name,
            slope_value,
            practical_threshold,
        )

        cv = coefficient_of_variation_percent(
            values
        )

        if (
            cv is not None
            and cv > 15.0
        ):
            direction = "high_variability"

        trends[
            feature_name
        ] = {
            "samples": len(values),
            "first_value": round(
                values[0],
                6,
            ),
            "latest_value": round(
                values[-1],
                6,
            ),
            "absolute_change": round(
                values[-1]
                - values[0],
                6,
            ),
            "slope_per_session": (
                round(
                    slope_value,
                    6,
                )
                if slope_value
                is not None
                else None
            ),
            "coefficient_of_variation_percent": (
                round(
                    cv,
                    2,
                )
                if cv is not None
                else None
            ),
            "direction": direction,
        }

    return {
        "status": (
            "completed"
            if trends
            else "insufficient_data"
        ),
        "trends": trends,
        "engine_version": "1.0.0",
    }
