from __future__ import annotations

from statistics import mean

from app.services.physics.models import (
    ImpulseState,
    PhysicsSample,
)


def _integrate_trapezoid(
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

        if dt <= 0:
            continue

        total += (
            values[index - 1]
            + values[index]
        ) * 0.5 * dt

    return total


def estimate_normalized_impulse(
    samples: list[PhysicsSample],
    *,
    start_ms: int,
    end_ms: int,
) -> ImpulseState | None:
    """
    Estimate mass-normalized impulse over a time window.

    This integrates COM acceleration over time, producing a change-in-
    velocity proxy. It is not equivalent to force-plate impulse.
    """

    window = [
        sample
        for sample in samples
        if start_ms <= sample.timestamp_ms <= end_ms
    ]

    if len(window) < 2:
        return None

    timestamps = [
        sample.timestamp_ms
        for sample in window
    ]

    horizontal = _integrate_trapezoid(
        timestamps,
        [
            sample.acceleration_x
            for sample in window
        ],
    )

    vertical = _integrate_trapezoid(
        timestamps,
        [
            sample.acceleration_y
            for sample in window
        ],
    )

    confidence = mean(
        sample.confidence
        for sample in window
    )

    return ImpulseState(
        start_ms=start_ms,
        end_ms=end_ms,
        duration_ms=end_ms - start_ms,
        normalized_horizontal_impulse=round(
            horizontal,
            6,
        ),
        normalized_vertical_impulse=round(
            vertical,
            6,
        ),
        confidence=round(
            max(
                0.0,
                min(
                    1.0,
                    confidence,
                ),
            ),
            4,
        ),
    )
