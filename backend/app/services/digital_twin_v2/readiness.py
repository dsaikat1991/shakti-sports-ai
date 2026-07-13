from __future__ import annotations

from typing import Any


def build_personal_readiness_summary(
    *,
    deviations: dict[str, Any],
    fatigue_signature: dict[str, Any],
    regressions: dict[str, Any],
    adaptations: dict[str, Any],
) -> dict[str, Any]:
    deviation_map = deviations.get(
        "deviations",
        {},
    )

    significant_deviations = sum(
        1
        for item
        in deviation_map.values()
        if item.get(
            "classification"
        )
        == "significant_deviation"
    )

    fatigue_penalty = (
        25.0
        if fatigue_signature.get(
            "pattern_detected"
        )
        else 0.0
    )

    regression_penalty = min(
        30.0,
        regressions.get(
            "count",
            0,
        )
        * 8.0,
    )

    deviation_penalty = min(
        20.0,
        significant_deviations
        * 5.0,
    )

    adaptation_bonus = min(
        10.0,
        adaptations.get(
            "count",
            0,
        )
        * 2.0,
    )

    score = max(
        0.0,
        min(
            100.0,
            90.0
            - fatigue_penalty
            - regression_penalty
            - deviation_penalty
            + adaptation_bonus,
        ),
    )

    return {
        "status": "experimental",
        "personal_readiness_score": (
            round(
                score,
                2,
            )
        ),
        "classification": (
            "high"
            if score >= 85.0
            else "moderate"
            if score >= 70.0
            else "low"
        ),
        "significant_deviations": (
            significant_deviations
        ),
        "fatigue_pattern_detected": bool(
            fatigue_signature.get(
                "pattern_detected"
            )
        ),
        "regression_count": (
            regressions.get(
                "count",
                0,
            )
        ),
        "adaptation_count": (
            adaptations.get(
                "count",
                0,
            )
        ),
        "engine_version": "1.0.0",
        "limitations": [
            "This is not medical clearance.",
            "The score reflects deviation from the athlete's own recent model.",
        ],
    }
