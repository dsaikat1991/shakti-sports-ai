from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


ValidationLevel = Literal[
    "validated",
    "research",
    "experimental",
    "estimated",
]


@dataclass(slots=True, frozen=True)
class PillarScore:
    name: str
    score: float | None
    weight: float
    confidence: float | None
    evidence: tuple[str, ...]
    penalties: tuple[str, ...]
    validation_level: ValidationLevel

    def weighted_score(self) -> float | None:
        if self.score is None:
            return None

        return self.score * self.weight

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence"] = list(self.evidence)
        payload["penalties"] = list(self.penalties)
        return payload


@dataclass(slots=True, frozen=True)
class MechanicalEfficiencyResult:
    score: float | None
    rating: str
    confidence: float | None
    pillars: tuple[PillarScore, ...]
    validation_level: ValidationLevel
    engine_version: str
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "rating": self.rating,
            "confidence": self.confidence,
            "pillars": [
                pillar.to_dict()
                for pillar in self.pillars
            ],
            "validation_level": self.validation_level,
            "engine_version": self.engine_version,
            "limitations": list(self.limitations),
        }
