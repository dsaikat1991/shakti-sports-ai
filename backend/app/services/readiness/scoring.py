from __future__ import annotations

from math import prod
from statistics import mean


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

    total_weight = sum(
        weight
        for _, weight in valid
    )

    if total_weight <= 0.0:
        return None

    return clamp_score(
        sum(
            value * weight
            for value, weight in valid
        )
        / total_weight
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

    return round(
        prod(valid)
        ** (
            1.0 / len(valid)
        ),
        4,
    )


def readiness_status(
    score: float | None,
) -> str:
    if score is None:
        return "insufficient_data"

    if score >= 95.0:
        return "peak_ready"
    if score >= 90.0:
        return "competition_ready"
    if score >= 80.0:
        return "ready"
    if score >= 70.0:
        return "monitor"
    if score >= 60.0:
        return "needs_recovery"

    return "not_recommended"


def inverse_risk_score(
    risk_percent: float | None,
) -> float | None:
    if risk_percent is None:
        return None

    return clamp_score(
        100.0 - risk_percent
    )


def stability_score(
    *,
    mechanical_efficiency_cv: float | None,
    cadence_cv: float | None,
    contact_cv: float | None,
) -> float | None:
    scores: list[
        tuple[
            float | None,
            float,
        ]
    ] = []

    for value, weight in (
        (
            mechanical_efficiency_cv,
            0.40,
        ),
        (
            cadence_cv,
            0.30,
        ),
        (
            contact_cv,
            0.30,
        ),
    ):
        if value is None:
            scores.append(
                (
                    None,
                    weight,
                )
            )
            continue

        scores.append(
            (
                clamp_score(
                    100.0
                    - min(
                        100.0,
                        value * 6.0,
                    )
                ),
                weight,
            )
        )

    return weighted_mean(
        scores
    )
