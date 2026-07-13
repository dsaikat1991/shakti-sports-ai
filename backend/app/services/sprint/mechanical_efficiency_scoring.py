from __future__ import annotations

from statistics import mean
from typing import Any


def clamp_score(
    value: float | None,
) -> float | None:
    if value is None:
        return None

    return round(
        max(
            0.0,
            min(
                100.0,
                float(value),
            ),
        ),
        2,
    )


def score_inverse_range(
    value: float | None,
    *,
    ideal_max: float,
    poor_max: float,
) -> float | None:
    if value is None:
        return None

    if poor_max <= ideal_max:
        raise ValueError(
            "poor_max must be greater than ideal_max."
        )

    if value <= ideal_max:
        return 100.0

    if value >= poor_max:
        return 0.0

    return clamp_score(
        100.0
        * (
            1.0
            - (
                value - ideal_max
            )
            / (
                poor_max - ideal_max
            )
        )
    )


def score_target_range(
    value: float | None,
    *,
    ideal_min: float,
    ideal_max: float,
    tolerance: float,
) -> float | None:
    if value is None:
        return None

    if ideal_max < ideal_min:
        raise ValueError(
            "ideal_max must be greater than or equal to ideal_min."
        )

    if tolerance <= 0:
        raise ValueError(
            "tolerance must be positive."
        )

    if ideal_min <= value <= ideal_max:
        return 100.0

    distance = (
        ideal_min - value
        if value < ideal_min
        else value - ideal_max
    )

    return clamp_score(
        100.0
        * (
            1.0
            - distance / tolerance
        )
    )


def weighted_mean(
    values: list[
        tuple[
            float | None,
            float,
        ]
    ],
) -> float | None:
    valid = [
        (
            float(value),
            max(
                0.0,
                float(weight),
            ),
        )
        for value, weight in values
        if value is not None
        and weight > 0.0
    ]

    if not valid:
        return None

    denominator = sum(
        weight
        for _, weight in valid
    )

    if denominator <= 0:
        return None

    return clamp_score(
        sum(
            value * weight
            for value, weight in valid
        )
        / denominator
    )


def geometric_confidence(
    values: list[float | None],
) -> float | None:
    valid = [
        max(
            1e-6,
            min(
                1.0,
                float(value),
            ),
        )
        for value in values
        if value is not None
    ]

    if not valid:
        return None

    product = 1.0

    for value in valid:
        product *= value

    return round(
        product ** (
            1.0 / len(valid)
        ),
        4,
    )


def rating_for_score(
    score: float | None,
) -> str:
    if score is None:
        return "insufficient_data"

    if score >= 90.0:
        return "excellent"
    if score >= 80.0:
        return "very_good"
    if score >= 70.0:
        return "good"
    if score >= 60.0:
        return "developing"
    if score >= 45.0:
        return "needs_improvement"

    return "poor"


def confidence_to_percent(
    value: float | None,
) -> float | None:
    if value is None:
        return None

    return round(
        max(
            0.0,
            min(
                1.0,
                value,
            ),
        )
        * 100.0,
        2,
    )
