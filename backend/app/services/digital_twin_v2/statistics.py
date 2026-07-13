from __future__ import annotations

from math import prod
from statistics import mean, median, pstdev


LOWER_IS_BETTER = {
    "ground_contact_ms",
    "braking_index",
    "vertical_oscillation_percent",
    "cadence_cv_percent",
    "contact_cv_percent",
    "flight_cv_percent",
    "mechanical_waste_index",
    "velocity_drop_percent",
    "back_side_duration_ms",
    "trailing_distance_percent",
}


def confidence_percent(
    values: list[float | None],
) -> float | None:
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


def slope(values: list[float]) -> float | None:
    if len(values) < 2:
        return None

    x_mean = (len(values) - 1) / 2.0
    y_mean = mean(values)

    numerator = sum(
        (index - x_mean) * (value - y_mean)
        for index, value in enumerate(values)
    )

    denominator = sum(
        (index - x_mean) ** 2
        for index in range(len(values))
    )

    if denominator <= 1e-12:
        return 0.0

    return float(numerator / denominator)


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


def summary(values: list[float]) -> dict:
    ordered = sorted(
        float(value)
        for value in values
    )

    if not ordered:
        return {
            "status": "insufficient_data",
        }

    return {
        "status": "completed",
        "samples": len(ordered),
        "mean": mean(ordered),
        "standard_deviation": (
            pstdev(ordered)
            if len(ordered) > 1
            else 0.0
        ),
        "minimum": ordered[0],
        "maximum": ordered[-1],
        "median": median(ordered),
    }


def performance_direction(
    feature_name: str,
    slope_value: float | None,
    practical_threshold: float,
) -> str:
    if slope_value is None:
        return "insufficient_data"

    if abs(slope_value) <= practical_threshold:
        return "stable"

    lower_is_better = (
        feature_name
        in LOWER_IS_BETTER
    )

    improving = (
        slope_value < 0.0
        if lower_is_better
        else slope_value > 0.0
    )

    return (
        "improving"
        if improving
        else "regressing"
    )
