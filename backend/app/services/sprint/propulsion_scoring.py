from __future__ import annotations

from math import prod


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


def integrate_trapezoid(
    timestamps_ms: list[int],
    values: list[float],
) -> float:
    if len(values) < 2:
        return 0.0

    total = 0.0

    for index in range(1, len(values)):
        dt = (
            timestamps_ms[index]
            - timestamps_ms[index - 1]
        ) / 1000.0

        if dt <= 0.0:
            continue

        total += (
            values[index - 1]
            + values[index]
        ) * 0.5 * dt

    return float(total)


def braking_index_from_areas(
    *,
    braking_area: float,
    propulsive_area: float,
) -> float:
    total = abs(braking_area) + abs(propulsive_area)

    if total <= 1e-12:
        return 0.0

    return round(
        abs(braking_area)
        / total
        * 100.0,
        2,
    )


def propulsion_score_from_areas(
    *,
    braking_area: float,
    propulsive_area: float,
) -> float:
    total = abs(braking_area) + abs(propulsive_area)

    if total <= 1e-12:
        return 0.0

    return round(
        clamp(
            abs(propulsive_area)
            / total
        )
        * 100.0,
        2,
    )


def net_propulsion_score(
    *,
    braking_index: float,
    propulsion_score: float,
    foot_offset_percent: float | None,
    shin_alignment_score: float | None,
) -> float:
    score = (
        propulsion_score * 0.55
        + (
            100.0 - braking_index
        ) * 0.25
    )

    if foot_offset_percent is not None:
        placement_score = (
            100.0
            * clamp(
                1.0
                - max(
                    0.0,
                    foot_offset_percent,
                )
                / 35.0
            )
        )

        score += placement_score * 0.10

    if shin_alignment_score is not None:
        score += shin_alignment_score * 0.10

    return round(
        max(
            0.0,
            min(
                100.0,
                score,
            ),
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


def quality_label(
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
    return "needs_improvement"
