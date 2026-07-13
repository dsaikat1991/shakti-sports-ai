from __future__ import annotations

from typing import Any

from app.services.biomechanics.gait_event_fusion import (
    EventCandidate,
    build_signal_vote,
    enforce_event_sequence,
    resolve_candidate,
)


CONTACT_THRESHOLD = 0.68
TOE_OFF_THRESHOLD = 0.64


def build_contact_candidate(
    *,
    side: str,
    timestamp_ms: int,
    frame_index: int,
    signals: dict[str, float],
    reliability: dict[str, float],
) -> EventCandidate:
    votes = (
        build_signal_vote(
            signal_name="foot_low",
            value=signals.get("foot_low", 0.0),
            reliability=reliability.get("foot", 0.0),
            weight=1.20,
            direction="high",
            threshold=0.55,
        ),
        build_signal_vote(
            signal_name="foot_speed_low",
            value=signals.get("foot_speed", 1.0),
            reliability=reliability.get("foot", 0.0),
            weight=1.00,
            direction="low",
            threshold=0.45,
        ),
        build_signal_vote(
            signal_name="ankle_acceleration",
            value=signals.get("ankle_acceleration", 0.0),
            reliability=reliability.get("ankle", 0.0),
            weight=1.10,
            direction="high",
            threshold=0.50,
        ),
        build_signal_vote(
            signal_name="knee_extension",
            value=signals.get("knee_extension", 0.0),
            reliability=reliability.get("knee", 0.0),
            weight=0.80,
            direction="high",
            threshold=0.50,
        ),
        build_signal_vote(
            signal_name="com_stability",
            value=signals.get("com_stability", 0.0),
            reliability=reliability.get("com", 0.0),
            weight=0.70,
            direction="high",
            threshold=0.45,
        ),
    )

    return EventCandidate(
        event_type="initial_contact",
        side=side,
        timestamp_ms=timestamp_ms,
        frame_index=frame_index,
        votes=votes,
    )


def build_toe_off_candidate(
    *,
    side: str,
    timestamp_ms: int,
    frame_index: int,
    signals: dict[str, float],
    reliability: dict[str, float],
) -> EventCandidate:
    votes = (
        build_signal_vote(
            signal_name="foot_upward_velocity",
            value=signals.get(
                "foot_upward_velocity",
                0.0,
            ),
            reliability=reliability.get("foot", 0.0),
            weight=1.25,
            direction="high",
            threshold=0.50,
        ),
        build_signal_vote(
            signal_name="foot_speed_high",
            value=signals.get("foot_speed", 0.0),
            reliability=reliability.get("foot", 0.0),
            weight=1.00,
            direction="high",
            threshold=0.50,
        ),
        build_signal_vote(
            signal_name="ankle_acceleration",
            value=signals.get("ankle_acceleration", 0.0),
            reliability=reliability.get("ankle", 0.0),
            weight=1.00,
            direction="high",
            threshold=0.45,
        ),
        build_signal_vote(
            signal_name="knee_angular_speed",
            value=signals.get("knee_angular_speed", 0.0),
            reliability=reliability.get("knee", 0.0),
            weight=0.85,
            direction="high",
            threshold=0.45,
        ),
        build_signal_vote(
            signal_name="hip_velocity",
            value=signals.get("hip_velocity", 0.0),
            reliability=reliability.get("hip", 0.0),
            weight=0.65,
            direction="high",
            threshold=0.40,
        ),
    )

    return EventCandidate(
        event_type="toe_off",
        side=side,
        timestamp_ms=timestamp_ms,
        frame_index=frame_index,
        votes=votes,
    )


def resolve_candidates(
    candidates: list[EventCandidate],
) -> dict[str, Any]:
    resolved = []

    for candidate in candidates:
        threshold = (
            CONTACT_THRESHOLD
            if candidate.event_type == "initial_contact"
            else TOE_OFF_THRESHOLD
        )

        resolved.append(
            resolve_candidate(
                candidate,
                threshold=threshold,
                minimum_supporting_signals=3,
            )
        )

    return enforce_event_sequence(
        resolved,
        minimum_gap_ms=60,
    )
