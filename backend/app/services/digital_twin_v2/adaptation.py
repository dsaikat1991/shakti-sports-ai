from __future__ import annotations

from typing import Any


def detect_adaptations(
    trends: dict[str, Any],
    deviations: dict[str, Any],
) -> dict[str, Any]:
    trend_map = trends.get(
        "trends",
        {},
    )

    deviation_map = deviations.get(
        "deviations",
        {},
    )

    adaptations = []

    for feature_name, trend in trend_map.items():
        if trend.get(
            "direction"
        ) != "improving":
            continue

        deviation = deviation_map.get(
            feature_name,
            {},
        )

        adaptations.append(
            {
                "feature_name": feature_name,
                "latest_value": trend.get(
                    "latest_value"
                ),
                "slope_per_session": trend.get(
                    "slope_per_session"
                ),
                "current_deviation_percent": (
                    deviation.get(
                        "deviation_percent"
                    )
                ),
                "classification": (
                    "established_adaptation"
                    if abs(
                        deviation.get(
                            "z_score"
                        )
                        or 0.0
                    )
                    >= 1.0
                    else "emerging_adaptation"
                ),
            }
        )

    adaptations.sort(
        key=lambda item: abs(
            item.get(
                "slope_per_session"
            )
            or 0.0
        ),
        reverse=True,
    )

    return {
        "status": (
            "completed"
            if adaptations
            else "insufficient_evidence"
        ),
        "adaptations": adaptations,
        "count": len(
            adaptations
        ),
        "engine_version": "1.0.0",
    }
