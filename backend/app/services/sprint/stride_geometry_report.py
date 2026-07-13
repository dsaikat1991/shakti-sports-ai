from __future__ import annotations

from typing import Any


def build_stride_geometry_report(
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
            "Stride geometry score: "
            f"{metrics.get('overall_stride_geometry_score')}"
        ),
        "summary": {
            "step_length_symmetry_score": (
                metrics.get(
                    "step_length_symmetry_score"
                )
            ),
            "geometry_stability_score": (
                metrics.get(
                    "geometry_stability_score"
                )
            ),
            "crossover_rate_percent": (
                metrics.get(
                    "crossover_rate_percent"
                )
            ),
            "optimal_step_length_difference_percent": (
                metrics.get(
                    "optimal_step_length_difference_percent"
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
            "validation_level"
        ),
        "engine_version": result.get(
            "engine_version"
        ),
    }
