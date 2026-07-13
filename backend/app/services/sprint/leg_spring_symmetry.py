from __future__ import annotations

from typing import Any


def build_leg_spring_symmetry(
    left_result: dict[str, Any],
    right_result: dict[str, Any],
) -> dict[str, Any]:
    left_metrics = left_result.get(
        "metrics"
    )

    right_metrics = right_result.get(
        "metrics"
    )

    if not left_metrics or not right_metrics:
        return {
            "status": "insufficient_data",
            "symmetry_score": None,
        }

    names = [
        "estimated_leg_compression_normalized",
        "elastic_return_ratio",
        "dynamic_leg_stiffness_index",
        "vertical_bounce_efficiency_score",
        "overall_leg_spring_score",
    ]

    component_scores: list[float] = []

    for name in names:
        left_value = left_metrics.get(name)
        right_value = right_metrics.get(name)

        if not isinstance(
            left_value,
            (int, float),
        ) or not isinstance(
            right_value,
            (int, float),
        ):
            continue

        denominator = max(
            abs(
                float(left_value)
            ),
            abs(
                float(right_value)
            ),
            1e-9,
        )

        component_scores.append(
            max(
                0.0,
                100.0
                * (
                    1.0
                    - abs(
                        float(left_value)
                        - float(right_value)
                    )
                    / denominator
                ),
            )
        )

    if not component_scores:
        return {
            "status": "insufficient_data",
            "symmetry_score": None,
        }

    return {
        "status": "completed",
        "symmetry_score": round(
            sum(component_scores)
            / len(component_scores),
            2,
        ),
        "components_used": len(
            component_scores
        ),
        "validation_level": (
            "experimental"
        ),
    }
