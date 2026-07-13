from __future__ import annotations

from typing import Any


def detect_regressions(
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

    regressions = []

    for feature_name, trend in trend_map.items():
        if trend.get(
            "direction"
        ) != "regressing":
            continue

        deviation = deviation_map.get(
            feature_name,
            {},
        )

        severity = "moderate"

        if abs(
            deviation.get(
                "z_score"
            )
            or 0.0
        ) >= 2.0:
            severity = "high"

        regressions.append(
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
                "severity": severity,
            }
        )

    regressions.sort(
        key=lambda item: (
            0
            if item["severity"]
            == "high"
            else 1,
            -abs(
                item.get(
                    "slope_per_session"
                )
                or 0.0
            ),
        )
    )

    return {
        "status": (
            "completed"
            if regressions
            else "insufficient_evidence"
        ),
        "regressions": regressions,
        "count": len(
            regressions
        ),
        "engine_version": "1.0.0",
    }
