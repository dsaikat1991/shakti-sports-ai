from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

EventType = Literal["initial_contact", "toe_off"]
Side = Literal["left", "right"]


@dataclass(slots=True, frozen=True)
class GaitEvent:
    event_type: EventType
    side: Side
    timestamp_ms: int
    frame_index: int | None = None
    confidence: float | None = None
    source: str = "unknown"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class EventMatch:
    predicted: GaitEvent
    actual: GaitEvent
    absolute_error_ms: int

    def to_dict(self) -> dict:
        return {
            "predicted": self.predicted.to_dict(),
            "actual": self.actual.to_dict(),
            "absolute_error_ms": self.absolute_error_ms,
        }