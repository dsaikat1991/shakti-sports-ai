from __future__ import annotations

from typing import Any


def build_propulsion_report(
    result: dict[str, Any],
) -> dict[str, Any]:
    metrics = result.get(
        "metrics"
    )

    if not metrics:
        return {
            "status": "insufficient_data",
        }

    score = metrics.get(
        "net_horizontal_propulsion_score"
    )

    braking_index = metrics.get(
        "braking_index"
    )

    propulsion_score = metrics.get(
        "propulsion_effectiveness_score"
    )

    return {
        "status": "completed",
        "headline": (
            f"Net horizontal propulsion score: {score}"
        ),
        "summary": (
            f"Estimated braking index is {braking_index}% "
            f"and propulsion effectiveness is {propulsion_score}%."
        ),
        "evidence": result.get(
            "evidence",
            [],
        ),
        "warnings": result.get(
            "warnings",
            [],
        ),
        "validation_level": result.get(
            "validation_level",
        ),
        "engine_version": result.get(
            "engine_version",
        ),
    }
