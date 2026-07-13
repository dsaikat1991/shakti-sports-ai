from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.services.biomechanics.gait_event_models import GaitEvent


@dataclass(slots=True, frozen=True)
class SignalVote:
    signal_name: str
    score: float
    reliability: float
    weight: float
    supports_event: bool

    def contribution(self) -> float:
        if not self.supports_event:
            return 0.0

        return (
            max(0.0, min(1.0, self.score))
            * max(0.0, min(1.0, self.reliability))
            * max(0.0, self.weight)
        )


@dataclass(slots=True, frozen=True)
class EventCandidate:
    event_type: str
    side: str
    timestamp_ms: int
    frame_index: int
    votes: tuple[SignalVote, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "side": self.side,
            "timestamp_ms": self.timestamp_ms,
            "frame_index": self.frame_index,
            "votes": [asdict(vote) for vote in self.votes],
        }


def fuse_votes(
    votes: tuple[SignalVote, ...],
    *,
    minimum_supporting_signals: int = 3,
) -> dict[str, Any]:
    supporting = [
        vote
        for vote in votes
        if vote.supports_event
        and vote.score > 0.0
        and vote.weight > 0.0
    ]

    if len(supporting) < minimum_supporting_signals:
        return {
            "status": "insufficient_support",
            "score": 0.0,
            "supporting_signals": [
                vote.signal_name for vote in supporting
            ],
            "support_count": len(supporting),
        }

    numerator = sum(
        vote.contribution()
        for vote in supporting
    )

    # Deliberately do not reliability-adjust the denominator.
    # Therefore weak reliability lowers the fused score.
    denominator = sum(
        max(0.0, vote.weight)
        for vote in supporting
    )

    weighted_score = (
        numerator / denominator
        if denominator > 0.0
        else 0.0
    )

    agreement = len(supporting) / max(len(votes), 1)

    calibrated = min(
        1.0,
        weighted_score * 0.90
        + agreement * 0.10,
    )

    return {
        "status": "fused",
        "score": round(calibrated, 4),
        "raw_weighted_score": round(weighted_score, 4),
        "agreement": round(agreement, 4),
        "supporting_signals": [
            vote.signal_name for vote in supporting
        ],
        "support_count": len(supporting),
    }


def resolve_candidate(
    candidate: EventCandidate,
    *,
    threshold: float,
    minimum_supporting_signals: int = 3,
    source: str = "multi_signal_fusion_v1",
) -> dict[str, Any]:
    fusion = fuse_votes(
        candidate.votes,
        minimum_supporting_signals=minimum_supporting_signals,
    )

    accepted = (
        fusion["status"] == "fused"
        and fusion["score"] >= threshold
    )

    event = None

    if accepted:
        event = GaitEvent(
            event_type=candidate.event_type,
            side=candidate.side,
            timestamp_ms=candidate.timestamp_ms,
            frame_index=candidate.frame_index,
            confidence=round(
                float(fusion["score"]) * 100.0,
                2,
            ),
            source=source,
        )

    return {
        "accepted": accepted,
        "event": event.to_dict() if event else None,
        "fusion": fusion,
        "candidate": candidate.to_dict(),
        "reason": (
            "threshold_met"
            if accepted
            else (
                "insufficient_support"
                if fusion["status"] == "insufficient_support"
                else "below_threshold"
            )
        ),
    }


def enforce_event_sequence(
    resolved_candidates: list[dict[str, Any]],
    *,
    minimum_gap_ms: int = 60,
) -> dict[str, Any]:
    ordered = sorted(
        resolved_candidates,
        key=lambda item: (
            int(item["candidate"]["timestamp_ms"]),
            0
            if item["candidate"]["event_type"]
            == "initial_contact"
            else 1,
        ),
    )

    side_state = {
        "left": "flight",
        "right": "flight",
    }

    last_event_ms = {
        "left": -10_000,
        "right": -10_000,
    }

    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for item in ordered:
        if not item["accepted"]:
            rejected.append(
                {
                    **item,
                    "sequence_reason": "candidate_not_accepted",
                }
            )
            continue

        candidate = item["candidate"]
        side = str(candidate["side"])
        event_type = str(candidate["event_type"])
        timestamp_ms = int(candidate["timestamp_ms"])

        if timestamp_ms - last_event_ms[side] < minimum_gap_ms:
            rejected.append(
                {
                    **item,
                    "sequence_reason": "minimum_gap_violation",
                }
            )
            continue

        expected = (
            "initial_contact"
            if side_state[side] == "flight"
            else "toe_off"
        )

        if event_type != expected:
            rejected.append(
                {
                    **item,
                    "sequence_reason": f"expected_{expected}",
                }
            )
            continue

        accepted.append(item)

        side_state[side] = (
            "stance"
            if event_type == "initial_contact"
            else "flight"
        )

        last_event_ms[side] = timestamp_ms

    events = [
        item["event"]
        for item in accepted
        if item.get("event") is not None
    ]

    return {
        "status": "completed" if events else "insufficient_data",
        "events": events,
        "accepted_candidates": accepted,
        "rejected_candidates": rejected,
        "final_state": side_state,
    }


def build_signal_vote(
    *,
    signal_name: str,
    value: float,
    reliability: float,
    weight: float,
    direction: str = "high",
    threshold: float = 0.5,
) -> SignalVote:
    normalized_value = max(
        0.0,
        min(1.0, float(value)),
    )

    if direction == "high":
        supports = normalized_value >= threshold
        score = normalized_value
    elif direction == "low":
        supports = normalized_value <= threshold
        score = 1.0 - normalized_value
    else:
        raise ValueError(
            "direction must be 'high' or 'low'."
        )

    return SignalVote(
        signal_name=signal_name,
        score=round(score, 4),
        reliability=round(
            max(0.0, min(1.0, reliability)),
            4,
        ),
        weight=round(max(0.0, weight), 4),
        supports_event=supports,
    )
