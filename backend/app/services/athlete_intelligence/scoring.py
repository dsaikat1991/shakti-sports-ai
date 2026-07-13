from __future__ import annotations

from math import prod
from statistics import mean, pstdev


LOWER_IS_BETTER = {
    "ground_contact_ms",
    "vertical_oscillation_percent",
    "braking_index",
    "cadence_cv_percent",
    "contact_cv_percent",
    "flight_cv_percent",
    "back_side_duration_ms",
    "trailing_distance_percent",
    "mechanical_waste_index",
    "velocity_drop_percent",
}


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, float(value)))


def confidence_percent(values: list[float | None]) -> float | None:
    valid = [
        max(1e-6, min(1.0, float(value)))
        for value in values
        if value is not None
    ]

    if not valid:
        return None

    return round(
        prod(valid) ** (1.0 / len(valid)) * 100.0,
        2,
    )


def weighted_score(
    values: list[tuple[float | None, float]],
) -> float | None:
    valid = [
        (float(value), float(weight))
        for value, weight in values
        if value is not None and weight > 0.0
    ]

    if not valid:
        return None

    denominator = sum(weight for _, weight in valid)

    return round(
        sum(value * weight for value, weight in valid)
        / denominator,
        2,
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


def trend_slope(values: list[float]) -> float | None:
    if len(values) < 2:
        return None

    x_mean = (len(values) - 1) / 2.0
    y_mean = mean(values)

    numerator = sum(
        (index - x_mean)
        * (value - y_mean)
        for index, value in enumerate(values)
    )

    denominator = sum(
        (index - x_mean) ** 2
        for index in range(len(values))
    )

    if denominator <= 1e-12:
        return 0.0

    return float(
        numerator / denominator
    )


def percentile_to_strength_score(
    percentile: float,
    *,
    lower_is_better: bool,
) -> float:
    return round(
        clamp(
            percentile
            if not lower_is_better
            else percentile
        ),
        2,
    )
