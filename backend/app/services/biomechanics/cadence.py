from __future__ import annotations

from statistics import mean, median
from typing import Any


def _peak_flexion_times(
    knee_cycle_events: dict[
        str,
        list[dict[str, int | float | str]],
    ],
) -> list[int]:
    timestamps: list[int] = []

    for side_events in knee_cycle_events.values():
        for event in side_events:
            if event.get("event") != "peak_flexion":
                continue

            timestamp = event.get("timestamp_ms")

            if isinstance(timestamp, int):
                timestamps.append(timestamp)

    return sorted(set(timestamps))


def estimate_cadence_from_knee_events(
    knee_cycle_events: dict[
        str,
        list[dict[str, int | float | str]],
    ],
) -> dict[str, Any]:
    """
    Estimate step cadence from alternating peak-knee-flexion events.

    This is experimental. Peak flexion is a timing proxy and is not
    equivalent to validated foot strike.
    """

    timestamps = _peak_flexion_times(knee_cycle_events)

    if len(timestamps) < 3:
        return {
            "status": "insufficient_data",
            "estimated_steps_per_minute": None,
            "average_step_interval_ms": None,
            "median_step_interval_ms": None,
            "events_used": len(timestamps),
            "method": "alternating_peak_knee_flexion_proxy",
        }

    intervals = [
        timestamps[index] - timestamps[index - 1]
        for index in range(1, len(timestamps))
        if timestamps[index] > timestamps[index - 1]
    ]

    plausible_intervals = [
        interval
        for interval in intervals
        if 120 <= interval <= 1000
    ]

    if len(plausible_intervals) < 2:
        return {
            "status": "low_confidence",
            "estimated_steps_per_minute": None,
            "average_step_interval_ms": None,
            "median_step_interval_ms": None,
            "events_used": len(timestamps),
            "method": "alternating_peak_knee_flexion_proxy",
        }

    average_interval = float(mean(plausible_intervals))
    median_interval = float(median(plausible_intervals))
    cadence_spm = 60000.0 / median_interval

    return {
        "status": "experimental",
        "estimated_steps_per_minute": round(cadence_spm, 2),
        "average_step_interval_ms": round(average_interval, 2),
        "median_step_interval_ms": round(median_interval, 2),
        "events_used": len(timestamps),
        "plausible_intervals_used": len(plausible_intervals),
        "method": "alternating_peak_knee_flexion_proxy",
        "warning": (
            "Cadence is estimated from knee-angle events and is not yet "
            "validated against foot-strike timing."
        ),
    }
