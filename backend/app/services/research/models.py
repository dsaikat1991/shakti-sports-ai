from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any

@dataclass(slots=True, frozen=True)
class ResearchRow:
    athlete_id: str | None
    performance_id: str
    event: str
    feature_name: str
    value: float | int | str | bool | None
    unit: str | None
    confidence: float | None
    side: str | None = None
    phase: str | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(slots=True, frozen=True)
class CohortDefinition:
    name: str
    filters: dict[str, Any]

@dataclass(slots=True, frozen=True)
class ComparisonResult:
    feature_name: str
    cohort_a: str
    cohort_b: str
    statistics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
