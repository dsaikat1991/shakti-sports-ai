from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.gait_event_models import GaitEvent
from app.services.biomechanics.gait_signals import (
    SideSignalSample,
    extract_side_signals,
)


@dataclass(slots=True)
class DetectorState:
    phase: str = "flight"
    last_event_ms: int = -10_000


def _normalise(
    values: list[float],
) -> list[float]:
    if not values:
        return []

    array = np.array(values, dtype=float)
    minimum = float(np.min(array))
    maximum = float(np.max(array))

    if maximum - minimum < 1e-9:
        return [0.5 for _ in values]

    return [
        float((value - minimum) / (maximum - minimum))
        for value in values
    ]


def _candidate_probabilities(
    samples: list[SideSignalSample],
) -> list[dict[str, Any]]:
    if not samples:
        return []

    foot_y_n = _normalise(
        [sample.foot_y for sample in samples]
    )
    foot_speed_n = _normalise(
        [sample.foot_speed for sample in samples]
    )
    acceleration_n = _normalise(
        [sample.ankle_acceleration for sample in samples]
    )

    knee_velocity_values = [
        abs(sample.knee_angular_velocity or 0.0)
        for sample in samples
    ]

    knee_velocity_n = _normalise(
        knee_velocity_values
    )

    candidates: list[dict[str, Any]] = []

    for index, sample in enumerate(samples):
        foot_low = foot_y_n[index]
        foot_slow = 1.0 - foot_speed_n[index]
        acceleration = acceleration_n[index]
        knee_stable = 1.0 - knee_velocity_n[index]

        downward_motion = max(
            0.0,
            sample.foot_vy,
        )

        upward_motion = max(
            0.0,
            -sample.foot_vy,
        )

        initial_contact_probability = (
            foot_low * 0.35
            + foot_slow * 0.25
            + acceleration * 0.20
            + knee_stable * 0.10
            + min(downward_motion * 2.0, 1.0) * 0.10
        )

        toe_off_probability = (
            foot_low * 0.20
            + acceleration * 0.20
            + min(upward_motion * 2.0, 1.0) * 0.35
            + foot_speed_n[index] * 0.15
            + knee_velocity_n[index] * 0.10
        )

        candidates.append(
            {
                "sample": sample,
                "initial_contact_probability": round(
                    float(initial_contact_probability),
                    4,
                ),
                "toe_off_probability": round(
                    float(toe_off_probability),
                    4,
                ),
                "supporting_signals": {
                    "foot_low": round(foot_low, 4),
                    "foot_slow": round(foot_slow, 4),
                    "ankle_acceleration": round(
                        acceleration,
                        4,
                    ),
                    "knee_stability": round(
                        knee_stable,
                        4,
                    ),
                },
            }
        )

    return candidates


def _detect_side_events(
    samples: list[SideSignalSample],
    *,
    contact_threshold: float = 0.68,
    toe_off_threshold: float = 0.62,
    minimum_event_gap_ms: int = 80,
) -> tuple[list[GaitEvent], list[dict[str, Any]]]:
    candidates = _candidate_probabilities(samples)
    state = DetectorState()
    events: list[GaitEvent] = []
    debug: list[dict[str, Any]] = []

    for candidate in candidates:
        sample: SideSignalSample = candidate["sample"]
        contact_probability = float(
            candidate[
                "initial_contact_probability"
            ]
        )
        toe_off_probability = float(
            candidate["toe_off_probability"]
        )

        event_type = None
        confidence = None

        if (
            state.phase == "flight"
            and contact_probability >= contact_threshold
            and (
                sample.timestamp_ms
                - state.last_event_ms
                >= minimum_event_gap_ms
            )
        ):
            event_type = "initial_contact"
            confidence = contact_probability
            state.phase = "stance"
            state.last_event_ms = sample.timestamp_ms

        elif (
            state.phase == "stance"
            and toe_off_probability >= toe_off_threshold
            and (
                sample.timestamp_ms
                - state.last_event_ms
                >= minimum_event_gap_ms
            )
        ):
            event_type = "toe_off"
            confidence = toe_off_probability
            state.phase = "flight"
            state.last_event_ms = sample.timestamp_ms

        if event_type is not None:
            events.append(
                GaitEvent(
                    event_type=event_type,
                    side=sample.side,
                    timestamp_ms=sample.timestamp_ms,
                    frame_index=sample.frame_index,
                    confidence=round(
                        confidence * 100.0,
                        2,
                    ),
                    source="multi_signal_state_machine_v2",
                )
            )

        debug.append(
            {
                "side": sample.side,
                "frame_index": sample.frame_index,
                "timestamp_ms": sample.timestamp_ms,
                "state": state.phase,
                "initial_contact_probability": (
                    contact_probability
                ),
                "toe_off_probability": (
                    toe_off_probability
                ),
                "supporting_signals": candidate[
                    "supporting_signals"
                ],
                "emitted_event": event_type,
            }
        )

    return events, debug


def detect_gait_events_v2(
    frame_metrics: list[FrameMetrics],
) -> dict[str, Any]:
    all_events: list[GaitEvent] = []
    debug: dict[str, list[dict[str, Any]]] = {
        "left": [],
        "right": [],
    }

    for side in ("left", "right"):
        samples = extract_side_signals(
            frame_metrics,
            side,
        )

        events, side_debug = _detect_side_events(
            samples
        )

        all_events.extend(events)
        debug[side] = side_debug

    all_events.sort(
        key=lambda event: event.timestamp_ms
    )

    return {
        "status": (
            "experimental"
            if all_events
            else "insufficient_data"
        ),
        "events": [
            event.to_dict()
            for event in all_events
        ],
        "counts": {
            "initial_contact": sum(
                1
                for event in all_events
                if event.event_type
                == "initial_contact"
            ),
            "toe_off": sum(
                1
                for event in all_events
                if event.event_type == "toe_off"
            ),
        },
        "method": (
            "multi_signal_probability_fusion_"
            "with_temporal_state_machine_v2"
        ),
        "debug": debug,
        "limitations": [
            "Thresholds are provisional and require calibration.",
            "The detector has not yet been benchmarked on labelled real sprint datasets.",
            "Event confidence is a fused heuristic probability, not a calibrated probability.",
        ],
    }
