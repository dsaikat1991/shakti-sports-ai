from __future__ import annotations

from dataclasses import dataclass

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.signal_processing import (
    AngleSample,
    prepare_angle_segments,
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

    # First pass: every strict turning point relative to its immediate
    # neighbours, regardless of size. A real running knee cycle often
    # wobbles by a frame or two right at the true peak, so the turning
    # point's *location* is still reliably its immediate neighbours -
    # it's only the *prominence* (how big a swing it represents) that
    # single-step comparison gets wrong.
    turning_points: list[tuple[str, AngleSample]] = []

    for index in range(1, len(series) - 1):
        previous_angle = series[index - 1].angle_degrees
        current = series[index]
        next_angle = series[index + 1].angle_degrees

        if (
            current.angle_degrees < previous_angle
            and current.angle_degrees <= next_angle
        ):
            turning_points.append(("minimum", current))
        elif (
            current.angle_degrees > previous_angle
            and current.angle_degrees >= next_angle
        ):
            turning_points.append(("maximum", current))

    # Second pass: prominence relative to the nearer of the two
    # surrounding opposite-type turning points (falling back to the
    # series' own edge when there isn't one on that side). This is how
    # far the signal actually swings around this extremum, rather than
    # the single-frame step used previously, which a brief plateau near
    # the true peak could shrink to near zero even for a large swing.
    events: list[KneeCycleEvent] = []

    for position, (kind, sample) in enumerate(turning_points):
        left_bound = (
            turning_points[position - 1][1].angle_degrees
            if position > 0
            else series[0].angle_degrees
        )
        right_bound = (
            turning_points[position + 1][1].angle_degrees
            if position < len(turning_points) - 1
            else series[-1].angle_degrees
        )

        if kind == "minimum":
            prominence = min(left_bound, right_bound) - sample.angle_degrees
            event_name = "peak_flexion"
        else:
            prominence = sample.angle_degrees - max(left_bound, right_bound)
            event_name = "peak_extension"

        if prominence >= minimum_prominence_degrees:
            events.append(
                KneeCycleEvent(
                    side=side,
                    event=event_name,
                    frame_index=sample.frame_index,
                    timestamp_ms=sample.timestamp_ms,
                    angle_degrees=round(sample.angle_degrees, 2),
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
        # Local extrema must be found within one contiguous segment: a
        # "previous"/"next" comparison across a timing gap would compare
        # samples that are not actually adjacent in time. Scan each
        # segment independently and merge, instead of only scanning the
        # single longest segment.
        events: list[KneeCycleEvent] = []
        for segment in prepare_angle_segments(frame_metrics, angle_name):
            events.extend(_find_local_extrema(segment, side=side))
        events.sort(key=lambda event: event.frame_index)

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
