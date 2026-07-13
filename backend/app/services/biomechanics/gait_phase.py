from __future__ import annotations

from dataclasses import dataclass

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.signal_processing import (
    AngleSample,
    prepare_angle_series,
    robust_angle_summary,
)


@dataclass(slots=True, frozen=True)
class KneeCycleEvent:
    side: str
    event: str
    frame_index: int
    timestamp_ms: int
    angle_degrees: float


def _find_local_extrema(
    series: list[AngleSample],
    *,
    side: str,
    minimum_prominence_degrees: float = 6.0,
) -> list[KneeCycleEvent]:
    if len(series) < 3:
        return []

    events: list[KneeCycleEvent] = []

    for index in range(1, len(series) - 1):
        previous_angle = series[index - 1].angle_degrees
        current = series[index]
        next_angle = series[index + 1].angle_degrees

        is_minimum = (
            current.angle_degrees < previous_angle
            and current.angle_degrees <= next_angle
        )
        is_maximum = (
            current.angle_degrees > previous_angle
            and current.angle_degrees >= next_angle
        )

        if is_minimum:
            prominence = min(
                previous_angle - current.angle_degrees,
                next_angle - current.angle_degrees,
            )
            if prominence >= minimum_prominence_degrees:
                events.append(
                    KneeCycleEvent(
                        side=side,
                        event="peak_flexion",
                        frame_index=current.frame_index,
                        timestamp_ms=current.timestamp_ms,
                        angle_degrees=round(current.angle_degrees, 2),
                    )
                )

        elif is_maximum:
            prominence = min(
                current.angle_degrees - previous_angle,
                current.angle_degrees - next_angle,
            )
            if prominence >= minimum_prominence_degrees:
                events.append(
                    KneeCycleEvent(
                        side=side,
                        event="peak_extension",
                        frame_index=current.frame_index,
                        timestamp_ms=current.timestamp_ms,
                        angle_degrees=round(current.angle_degrees, 2),
                    )
                )

    return events


def detect_knee_cycle_events(
    frame_metrics: list[FrameMetrics],
) -> dict[str, list[dict[str, int | float | str]]]:
    result: dict[str, list[dict[str, int | float | str]]] = {
        "left": [],
        "right": [],
    }

    for side, angle_name in (
        ("left", "left_knee"),
        ("right", "right_knee"),
    ):
        prepared_series = prepare_angle_series(
            frame_metrics,
            angle_name,
        )
        events = _find_local_extrema(
            prepared_series,
            side=side,
        )

        result[side] = [
            {
                "side": event.side,
                "event": event.event,
                "frame_index": event.frame_index,
                "timestamp_ms": event.timestamp_ms,
                "angle_degrees": event.angle_degrees,
            }
            for event in events
        ]

    return result


def calculate_knee_symmetry(
    frame_metrics: list[FrameMetrics],
) -> dict[str, float | int | str | None]:
    left_series = prepare_angle_series(
        frame_metrics,
        "left_knee",
    )
    right_series = prepare_angle_series(
        frame_metrics,
        "right_knee",
    )

    left_summary = robust_angle_summary(left_series)
    right_summary = robust_angle_summary(right_series)

    left_range = left_summary["range_degrees"]
    right_range = right_summary["range_degrees"]

    if left_range is None or right_range is None:
        return {
            "left_range_degrees": None,
            "right_range_degrees": None,
            "range_difference_degrees": None,
            "symmetry_score": None,
            "paired_frames": 0,
            "status": "insufficient_data",
        }

    difference = abs(float(left_range) - float(right_range))
    reference_range = max(float(left_range), float(right_range), 1.0)
    symmetry_score = max(
        0.0,
        100.0 - difference / reference_range * 100.0,
    )
    paired_frames = min(len(left_series), len(right_series))

    return {
        "left_range_degrees": round(float(left_range), 2),
        "right_range_degrees": round(float(right_range), 2),
        "range_difference_degrees": round(difference, 2),
        "symmetry_score": round(symmetry_score, 2),
        "paired_frames": paired_frames,
        "status": (
            "experimental"
            if paired_frames >= 10
            else "low_confidence"
        ),
    }
