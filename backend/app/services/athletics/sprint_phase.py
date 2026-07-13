from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any

import numpy as np


@dataclass(slots=True, frozen=True)
class SprintPhase:
    name: str
    start_ms: int
    end_ms: int
    duration_ms: int
    confidence: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _moving_average(
    values: list[float],
    window_size: int = 5,
) -> list[float]:
    if not values:
        return []

    if window_size <= 1 or len(values) < 3:
        return values.copy()

    if window_size % 2 == 0:
        window_size += 1

    radius = window_size // 2
    smoothed: list[float] = []

    for index in range(len(values)):
        start = max(0, index - radius)
        end = min(len(values), index + radius + 1)

        smoothed.append(
            float(np.mean(values[start:end]))
        )

    return smoothed


def _normalise(
    values: list[float],
) -> list[float]:
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


def _derivative(
    timestamps_ms: list[int],
    values: list[float],
) -> list[float]:
    if len(values) != len(timestamps_ms):
        raise ValueError(
            "timestamps_ms and values must have equal length."
        )

    if not values:
        return []

    result = [0.0]

    for index in range(1, len(values)):
        dt = (
            timestamps_ms[index]
            - timestamps_ms[index - 1]
        ) / 1000.0

        if dt <= 0:
            result.append(0.0)
            continue

        result.append(
            (values[index] - values[index - 1]) / dt
        )

    return result


def _first_sustained_index(
    values: list[float],
    *,
    threshold: float,
    window_size: int = 3,
    mode: str = "above",
) -> int | None:
    if len(values) < window_size:
        return None

    for start in range(
        0,
        len(values) - window_size + 1,
    ):
        window = values[
            start:start + window_size
        ]

        if mode == "above":
            matched = all(
                value >= threshold
                for value in window
            )
        elif mode == "below":
            matched = all(
                value <= threshold
                for value in window
            )
        else:
            raise ValueError(
                "mode must be 'above' or 'below'."
            )

        if matched:
            return start

    return None


def detect_sprint_phases(
    *,
    timestamps_ms: list[int],
    horizontal_progression: list[float],
    cadence_values: list[float] | None = None,
    contact_time_values: list[float] | None = None,
) -> dict[str, Any]:
    """
    Detect coarse sprint phases from motion progression.

    This first version is intentionally conservative and produces:
    - acceleration
    - transition
    - maximum_velocity
    - maintenance
    - deceleration

    Reaction and block exit require start-specific inputs and are not
    independently detected yet.
    """

    if (
        len(timestamps_ms) < 8
        or len(horizontal_progression)
        != len(timestamps_ms)
    ):
        return {
            "status": "insufficient_data",
            "phases": [],
            "confidence": 0.0,
        }

    smoothed_position = _moving_average(
        horizontal_progression,
        window_size=5,
    )

    velocity = _moving_average(
        _derivative(
            timestamps_ms,
            smoothed_position,
        ),
        window_size=5,
    )

    acceleration = _moving_average(
        _derivative(
            timestamps_ms,
            velocity,
        ),
        window_size=5,
    )

    velocity_n = _normalise(
        [abs(value) for value in velocity]
    )

    acceleration_n = _normalise(
        acceleration
    )

    peak_velocity_index = int(
        np.argmax(velocity_n)
    )

    acceleration_end_index = (
        _first_sustained_index(
            velocity_n,
            threshold=0.55,
            window_size=3,
            mode="above",
        )
    )

    if acceleration_end_index is None:
        acceleration_end_index = max(
            1,
            peak_velocity_index // 2,
        )

    transition_end_index = max(
        acceleration_end_index + 1,
        min(
            peak_velocity_index,
            len(timestamps_ms) - 1,
        ),
    )

    maintenance_start_index = (
        _first_sustained_index(
            velocity_n[
                transition_end_index:
            ],
            threshold=0.85,
            window_size=3,
            mode="above",
        )
    )

    if maintenance_start_index is None:
        maintenance_start_index = (
            transition_end_index
        )
    else:
        maintenance_start_index += (
            transition_end_index
        )

    deceleration_relative = (
        _first_sustained_index(
            velocity_n[
                maintenance_start_index:
            ],
            threshold=0.65,
            window_size=3,
            mode="below",
        )
    )

    if deceleration_relative is None:
        deceleration_start_index = (
            len(timestamps_ms) - 1
        )
    else:
        deceleration_start_index = (
            maintenance_start_index
            + deceleration_relative
        )

    phase_boundaries = [
        (
            "acceleration",
            0,
            acceleration_end_index,
            "Velocity rises toward sustainable sprint speed.",
        ),
        (
            "transition",
            acceleration_end_index,
            transition_end_index,
            "Acceleration reduces while velocity approaches its peak.",
        ),
        (
            "maximum_velocity",
            transition_end_index,
            maintenance_start_index,
            "Highest observed velocity region.",
        ),
        (
            "maintenance",
            maintenance_start_index,
            deceleration_start_index,
            "Velocity remains comparatively stable.",
        ),
        (
            "deceleration",
            deceleration_start_index,
            len(timestamps_ms) - 1,
            "Velocity falls below the maintenance region.",
        ),
    ]

    phases: list[SprintPhase] = []

    for name, start_index, end_index, reason in phase_boundaries:
        if end_index <= start_index:
            continue

        start_ms = int(
            timestamps_ms[start_index]
        )
        end_ms = int(
            timestamps_ms[end_index]
        )

        local_velocity = velocity_n[
            start_index:end_index + 1
        ]

        local_variability = (
            float(np.std(local_velocity))
            if local_velocity
            else 1.0
        )

        confidence = max(
            0.35,
            min(
                0.95,
                0.90 - local_variability * 0.50,
            ),
        )

        phases.append(
            SprintPhase(
                name=name,
                start_ms=start_ms,
                end_ms=end_ms,
                duration_ms=end_ms - start_ms,
                confidence=round(
                    confidence * 100.0,
                    2,
                ),
                reason=reason,
            )
        )

    cadence_summary = None

    if (
        cadence_values is not None
        and len(cadence_values)
        == len(timestamps_ms)
    ):
        cadence_summary = {
            phase.name: round(
                mean(
                    cadence_values[
                        max(
                            0,
                            np.searchsorted(
                                timestamps_ms,
                                phase.start_ms,
                            ),
                        ):
                        min(
                            len(cadence_values),
                            np.searchsorted(
                                timestamps_ms,
                                phase.end_ms,
                                side="right",
                            ),
                        )
                    ]
                ),
                3,
            )
            for phase in phases
            if np.searchsorted(
                timestamps_ms,
                phase.end_ms,
                side="right",
            )
            > np.searchsorted(
                timestamps_ms,
                phase.start_ms,
            )
        }

    contact_summary = None

    if (
        contact_time_values is not None
        and len(contact_time_values)
        == len(timestamps_ms)
    ):
        contact_summary = {
            phase.name: round(
                mean(
                    contact_time_values[
                        max(
                            0,
                            np.searchsorted(
                                timestamps_ms,
                                phase.start_ms,
                            ),
                        ):
                        min(
                            len(contact_time_values),
                            np.searchsorted(
                                timestamps_ms,
                                phase.end_ms,
                                side="right",
                            ),
                        )
                    ]
                ),
                2,
            )
            for phase in phases
            if np.searchsorted(
                timestamps_ms,
                phase.end_ms,
                side="right",
            )
            > np.searchsorted(
                timestamps_ms,
                phase.start_ms,
            )
        }

    overall_confidence = (
        round(
            mean(
                phase.confidence
                for phase in phases
            ),
            2,
        )
        if phases
        else 0.0
    )

    return {
        "status": (
            "experimental"
            if phases
            else "insufficient_data"
        ),
        "phases": [
            phase.to_dict()
            for phase in phases
        ],
        "overall_confidence": (
            overall_confidence
        ),
        "derived_signals": {
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
            "normalized_acceleration": [
                round(value, 6)
                for value in acceleration_n
            ],
        },
        "phase_metric_preview": {
            "cadence": cadence_summary,
            "contact_time": contact_summary,
        },
        "limitations": [
            "Reaction and block-exit phases are not independently detected.",
            "Phase boundaries are camera-relative and require validation against labelled sprint clips.",
            "The detector is intended for side-view sprint video.",
        ],
    }
