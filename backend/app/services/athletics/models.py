from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


AthleticsEvent = Literal[
    "sprint",
    "hurdles",
    "long_jump",
    "high_jump",
]


@dataclass(slots=True, frozen=True)
class EventAnalysisRequest:
    event: AthleticsEvent
    athlete_id: str | None = None
    performance_id: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(slots=True, frozen=True)
class EventAnalysisResult:
    event: AthleticsEvent
    status: str
    readiness: dict[str, Any]
    phases: dict[str, Any]
    metrics: dict[str, Any]
    limitations: tuple[str, ...]
    analyzer_version: str

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["limitations"] = list(self.limitations)
        return result
