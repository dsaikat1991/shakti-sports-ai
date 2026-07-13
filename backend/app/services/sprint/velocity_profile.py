from __future__ import annotations

from typing import Any

import numpy as np

from app.services.sprint.phase_models import SprintSignalFrame


def _normalise(values: list[float]) -> list[float]:
    if not values:
        return []

    array = np.asarray(values, dtype=float)
    low = float(np.percentile(array, 5))
    high = float(np.percentile(array, 95))

    if high - low < 1e-9:
        return [0.0 for _ in values]

    return [
        float(
            np.clip(
                (value - low) / (high - low),
                0.0,
                1.0,
            )
        )
        for value in values
    ]


def moving_average(
    values: list[float],
    *,
    window_size: int = 5,
) -> list[float]:
    if not values:
        return []

    if window_size <= 1:
        return values.copy()

    if window_size % 2 == 0:
        window_size += 1

    radius = window_size // 2

    return [
        float(
            np.mean(
                values[
                    max(0, index - radius):
                    min(len(values), index + radius + 1)
                ]
            )
        )
        for index in range(len(values))
    ]


def build_velocity_profile(
    frames: list[SprintSignalFrame],
    *,
    smoothing_window: int = 5,
) -> dict[str, Any]:
    if len(frames) < 5:
        return {
            "status": "insufficient_data",
        }

    ordered = sorted(
        frames,
        key=lambda frame: frame.timestamp_ms,
    )

    velocity = moving_average(
        [
            frame.com_velocity_x
            for frame in ordered
        ],
        window_size=smoothing_window,
    )

    acceleration = moving_average(
        [
            frame.com_acceleration_x
            for frame in ordered
        ],
        window_size=smoothing_window,
    )

    velocity_n = _normalise(
        [abs(value) for value in velocity]
    )

    positive_acceleration_n = _normalise(
        [
            max(0.0, value)
            for value in acceleration
        ]
    )

    peak_velocity_index = int(
        np.argmax(velocity_n)
    )

    return {
        "status": "completed",
        "timestamps_ms": [
            frame.timestamp_ms
            for frame in ordered
        ],
        "frame_indices": [
            frame.frame_index
            for frame in ordered
        ],
        "velocity": [
            round(value, 6)
            for value in velocity
        ],
        "acceleration": [
            round(value, 6)
            for value in acceleration
        ],
        "normalized_velocity": [
            round(value, 6)
            for value in velocity_n
        ],
        "normalized_positive_acceleration": [
            round(value, 6)
            for value in positive_acceleration_n
        ],
        "peak_velocity_index": peak_velocity_index,
        "peak_velocity_frame": ordered[
            peak_velocity_index
        ].frame_index,
        "peak_velocity_timestamp_ms": ordered[
            peak_velocity_index
        ].timestamp_ms,
    }
