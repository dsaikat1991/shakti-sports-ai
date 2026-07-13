from __future__ import annotations

from math import atan2, degrees, prod
from statistics import mean, pstdev


def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    return max(
        minimum,
        min(
            maximum,
            float(value),
        ),
    )


def safe_mean(
    values: list[float],
) -> float | None:
    if not values:
        return None

    return float(
        mean(values)
    )


def coefficient_of_variation_percent(
    values: list[float],
) -> float | None:
    if len(values) < 2:
        return None

    average = mean(values)

    if abs(average) <= 1e-12:
        return None

    return float(
        pstdev(values)
        / abs(average)
        * 100.0
    )


def inverse_cv_score(
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

    return round(
        (
            1.0
            - (
                value - ideal_max
            )
            / (
                poor_max - ideal_max
            )
        )
        * 100.0,
        2,
    )


def symmetry_score(
    left_value: float | None,
    right_value: float | None,
) -> float | None:
    if (
        left_value is None
        or right_value is None
    ):
        return None

    denominator = max(
        abs(left_value),
        abs(right_value),
        1e-12,
    )

    return round(
        clamp(
            1.0
            - abs(
                left_value
                - right_value
            )
            / denominator
        )
        * 100.0,
        2,
    )


def target_score(
    value: float | None,
    *,
    ideal_min: float,
    ideal_max: float,
    tolerance: float,
) -> float | None:
    if value is None:
        return None

    if ideal_min <= value <= ideal_max:
        return 100.0

    distance = (
        ideal_min - value
        if value < ideal_min
        else value - ideal_max
    )

    return round(
        clamp(
            1.0
            - distance / tolerance
        )
        * 100.0,
        2,
    )


def toe_direction_deg(
    *,
    heel_x: float | None,
    heel_y: float | None,
    toe_x: float | None,
    toe_y: float | None,
) -> float | None:
    if (
        heel_x is None
        or heel_y is None
        or toe_x is None
        or toe_y is None
    ):
        return None

    return round(
        degrees(
            atan2(
                toe_y - heel_y,
                toe_x - heel_x,
            )
        ),
        2,
    )


def confidence_percent(
    values: list[float],
) -> float | None:
    bounded = [
        clamp(value)
        for value in values
    ]

    if not bounded:
        return None

    return round(
        prod(bounded)
        ** (
            1.0 / len(bounded)
        )
        * 100.0,
        2,
    )


def weighted_score(
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
            float(weight),
        )
        for value, weight in values
        if value is not None
        and weight > 0.0
    ]

    if not valid:
        return None

    total_weight = sum(
        weight
        for _, weight in valid
    )

    return round(
        sum(
            value * weight
            for value, weight in valid
        )
        / total_weight,
        2,
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
