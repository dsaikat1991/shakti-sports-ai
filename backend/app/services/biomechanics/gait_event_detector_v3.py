from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from app.services.biomechanics.frame_metrics import FrameMetrics
from app.services.biomechanics.gait_detector_config import (
    GaitDetectorConfig,
)
from app.services.biomechanics.gait_event_models import GaitEvent
from app.services.biomechanics.gait_signals import (
    SideSignalSample,
    extract_side_signals,
)


@dataclass(slots=True, frozen=True)
class Candidate:
    side: str
    event_type: str
    timestamp_ms: int
    frame_index: int
    raw_score: float
    calibrated_score: float
    supporting_signals: dict[str, float]


@dataclass(slots=True)
class GlobalState:
    last_contact_side: str | None = None
    last_contact_ms: int = -10_000
    last_toe_off_ms: dict[str, int] | None = None
    in_stance: dict[str, bool] | None = None

    def __post_init__(self) -> None:
        if self.last_toe_off_ms is None:
            self.last_toe_off_ms = {
                "left": -10_000,
                "right": -10_000,
            }

        if self.in_stance is None:
            self.in_stance = {
                "left": False,
                "right": False,
            }


def _normalise(values: list[float]) -> list[float]:
    if not values:
        return []

    array = np.asarray(values, dtype=float)
    low = float(np.percentile(array, 5))
    high = float(np.percentile(array, 95))

    if high - low < 1e-9:
        return [0.5 for _ in values]

    return [
        float(np.clip((value - low) / (high - low), 0.0, 1.0))
        for value in values
    ]


def _local_peak(
    values: list[float],
    index: int,
    radius: int,
) -> bool:
    start = max(0, index - radius)
    end = min(len(values), index + radius + 1)
    window = values[start:end]

    return values[index] == max(window)


def _build_side_candidates(
    samples: list[SideSignalSample],
    config: GaitDetectorConfig,
) -> list[Candidate]:
    if len(samples) < 5:
        return []

    foot_y = _normalise(
        [sample.foot_y for sample in samples]
    )
    foot_speed = _normalise(
        [sample.foot_speed for sample in samples]
    )
    ankle_acceleration = _normalise(
        [sample.ankle_acceleration for sample in samples]
    )
    knee_speed = _normalise(
        [
            abs(sample.knee_angular_velocity or 0.0)
            for sample in samples
        ]
    )
    hip_speed = _normalise(
        [
            abs(sample.hip_vy or 0.0)
            for sample in samples
        ]
    )
    com_speed = _normalise(
        [
            abs(sample.com_vy or 0.0)
            for sample in samples
        ]
    )

    contact_scores: list[float] = []
    toe_off_scores: list[float] = []

    for index, sample in enumerate(samples):
        foot_low = foot_y[index]
        foot_slow = 1.0 - foot_speed[index]
        knee_stable = 1.0 - knee_speed[index]
        hip_stable = 1.0 - hip_speed[index]
        com_stable = 1.0 - com_speed[index]

        downward = min(max(sample.foot_vy, 0.0) * 2.5, 1.0)
        upward = min(max(-sample.foot_vy, 0.0) * 2.5, 1.0)

        contact_score = (
            foot_low * 0.28
            + foot_slow * 0.20
            + ankle_acceleration[index] * 0.18
            + knee_stable * 0.10
            + hip_stable * 0.08
            + com_stable * 0.08
            + downward * 0.08
        )

        toe_off_score = (
            foot_low * 0.16
            + foot_speed[index] * 0.18
            + ankle_acceleration[index] * 0.18
            + knee_speed[index] * 0.12
            + hip_speed[index] * 0.08
            + upward * 0.28
        )

        contact_scores.append(float(contact_score))
        toe_off_scores.append(float(toe_off_score))

    candidates: list[Candidate] = []

    for index, sample in enumerate(samples):
        signals = {
            "foot_low": round(foot_y[index], 4),
            "foot_slow": round(1.0 - foot_speed[index], 4),
            "ankle_acceleration": round(
                ankle_acceleration[index],
                4,
            ),
            "knee_speed": round(knee_speed[index], 4),
            "hip_speed": round(hip_speed[index], 4),
            "com_speed": round(com_speed[index], 4),
        }

        if (
            contact_scores[index] >= config.contact_threshold
            and _local_peak(
                contact_scores,
                index,
                config.local_peak_radius,
            )
        ):
            candidates.append(
                Candidate(
                    side=sample.side,
                    event_type="initial_contact",
                    timestamp_ms=sample.timestamp_ms,
                    frame_index=sample.frame_index,
                    raw_score=contact_scores[index],
                    calibrated_score=contact_scores[index],
                    supporting_signals=signals,
                )
            )

        if (
            toe_off_scores[index] >= config.toe_off_threshold
            and _local_peak(
                toe_off_scores,
                index,
                config.local_peak_radius,
            )
        ):
            candidates.append(
                Candidate(
                    side=sample.side,
                    event_type="toe_off",
                    timestamp_ms=sample.timestamp_ms,
                    frame_index=sample.frame_index,
                    raw_score=toe_off_scores[index],
                    calibrated_score=toe_off_scores[index],
                    supporting_signals=signals,
                )
            )

    return candidates


def _apply_temporal_context(
    candidate: Candidate,
    state: GlobalState,
    config: GaitDetectorConfig,
) -> Candidate:
    score = candidate.raw_score

    if candidate.event_type == "initial_contact":
        if (
            state.last_contact_side is not None
            and state.last_contact_side != candidate.side
        ):
            score += config.alternation_bonus

        elif state.last_contact_side == candidate.side:
            elapsed = (
                candidate.timestamp_ms
                - state.last_contact_ms
            )

            if elapsed < config.minimum_same_side_stride_ms:
                score -= config.same_side_penalty

            elif elapsed > config.maximum_same_side_stride_ms:
                score -= config.same_side_penalty / 2.0

    elif candidate.event_type == "toe_off":
        if not state.in_stance[candidate.side]:
            score -= 0.20

    return Candidate(
        side=candidate.side,
        event_type=candidate.event_type,
        timestamp_ms=candidate.timestamp_ms,
        frame_index=candidate.frame_index,
        raw_score=candidate.raw_score,
        calibrated_score=float(
            np.clip(score, 0.0, 1.0)
        ),
        supporting_signals=candidate.supporting_signals,
    )


def detect_gait_events_v3(
    frame_metrics: list[FrameMetrics],
    *,
    config: GaitDetectorConfig | None = None,
    include_debug: bool = True,
) -> dict[str, Any]:
    detector_config = config or GaitDetectorConfig()

    candidates: list[Candidate] = []

    for side in ("left", "right"):
        samples = extract_side_signals(
            frame_metrics,
            side,
        )

        candidates.extend(
            _build_side_candidates(
                samples,
                detector_config,
            )
        )

    candidates.sort(
        key=lambda item: (
            item.timestamp_ms,
            0 if item.event_type == "initial_contact" else 1,
            -item.raw_score,
        )
    )

    state = GlobalState()
    events: list[GaitEvent] = []
    accepted_debug: list[dict[str, Any]] = []
    rejected_debug: list[dict[str, Any]] = []

    for raw_candidate in candidates:
        candidate = _apply_temporal_context(
            raw_candidate,
            state,
            detector_config,
        )

        threshold = (
            detector_config.contact_threshold
            if candidate.event_type == "initial_contact"
            else detector_config.toe_off_threshold
        )

        reason = None

        if candidate.calibrated_score < threshold:
            reason = "below_threshold_after_temporal_context"

        elif (
            events
            and candidate.timestamp_ms
            - events[-1].timestamp_ms
            < detector_config.minimum_event_gap_ms
        ):
            reason = "global_refractory_period"

        elif (
            candidate.event_type == "initial_contact"
            and state.in_stance[candidate.side]
        ):
            reason = "side_already_in_stance"

        elif (
            candidate.event_type == "toe_off"
            and not state.in_stance[candidate.side]
        ):
            reason = "toe_off_without_prior_contact"

        if reason is not None:
            rejected_debug.append(
                {
                    "candidate": candidate,
                    "reason": reason,
                }
            )
            continue

        event = GaitEvent(
            event_type=candidate.event_type,
            side=candidate.side,
            timestamp_ms=candidate.timestamp_ms,
            frame_index=candidate.frame_index,
            confidence=round(
                candidate.calibrated_score * 100.0,
                2,
            ),
            source="multi_signal_global_state_machine_v3",
        )

        events.append(event)

        if candidate.event_type == "initial_contact":
            state.in_stance[candidate.side] = True
            state.last_contact_side = candidate.side
            state.last_contact_ms = candidate.timestamp_ms
        else:
            state.in_stance[candidate.side] = False
            state.last_toe_off_ms[candidate.side] = (
                candidate.timestamp_ms
            )

        accepted_debug.append(
            {
                "event": event.to_dict(),
                "raw_score": round(candidate.raw_score, 4),
                "calibrated_score": round(
                    candidate.calibrated_score,
                    4,
                ),
                "supporting_signals": (
                    candidate.supporting_signals
                ),
            }
        )

    result = {
        "status": (
            "experimental"
            if events
            else "insufficient_data"
        ),
        "events": [
            event.to_dict()
            for event in events
        ],
        "counts": {
            "initial_contact": sum(
                event.event_type == "initial_contact"
                for event in events
            ),
            "toe_off": sum(
                event.event_type == "toe_off"
                for event in events
            ),
        },
        "method": "multi_signal_global_state_machine_v3",
        "config": {
            "contact_threshold": (
                detector_config.contact_threshold
            ),
            "toe_off_threshold": (
                detector_config.toe_off_threshold
            ),
            "minimum_event_gap_ms": (
                detector_config.minimum_event_gap_ms
            ),
            "minimum_same_side_stride_ms": (
                detector_config.minimum_same_side_stride_ms
            ),
            "maximum_same_side_stride_ms": (
                detector_config.maximum_same_side_stride_ms
            ),
        },
        "limitations": [
            "Thresholds remain provisional.",
            "Confidence is not yet statistically calibrated.",
            "The detector must be benchmarked against labelled sprint videos before replacing the current production proxy.",
        ],
    }

    if include_debug:
        result["debug"] = {
            "accepted": accepted_debug,
            "rejected": [
                {
                    "candidate": {
                        "side": item["candidate"].side,
                        "event_type": (
                            item["candidate"].event_type
                        ),
                        "timestamp_ms": (
                            item["candidate"].timestamp_ms
                        ),
                        "frame_index": (
                            item["candidate"].frame_index
                        ),
                        "raw_score": round(
                            item["candidate"].raw_score,
                            4,
                        ),
                        "calibrated_score": round(
                            item["candidate"].calibrated_score,
                            4,
                        ),
                    },
                    "reason": item["reason"],
                }
                for item in rejected_debug
            ],
        }

    return result
