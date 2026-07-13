from __future__ import annotations

from typing import Any


def build_leg_spring_report(
    result: dict[str, Any],
) -> dict[str, Any]:
    metrics = result.get(
        "metrics"
    )

    if not metrics:
        return {
            "status": "insufficient_data",
        }

    return {
        "status": "completed",
        "headline": (
            "Leg spring score: "
            f"{metrics.get('overall_leg_spring_score')}"
        ),
        "summary": {
            "compression": metrics.get(
                "estimated_leg_compression_normalized"
            ),
            "elastic_return_ratio": (
                metrics.get(
                    "elastic_return_ratio"
                )
            ),
            "dynamic_leg_stiffness_index": (
                metrics.get(
                    "dynamic_leg_stiffness_index"
                )
            ),
            "vertical_bounce_efficiency_score": (
                metrics.get(
                    "vertical_bounce_efficiency_score"
                )
            ),
        },
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
