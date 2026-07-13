from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


ReadinessStatus = Literal[
    "peak_ready",
    "competition_ready",
    "ready",
    "monitor",
    "needs_recovery",
    "not_recommended",
    "insufficient_data",
]


@dataclass(slots=True, frozen=True)
class ReadinessComponent:
    name: str
    score: float | None
    weight: float
    confidence: float | None
    evidence: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["evidence"] = list(self.evidence)
        result["warnings"] = list(self.warnings)
        return result


@dataclass(slots=True, frozen=True)
class CompetitionReadinessResult:
    score: float | None
    status: ReadinessStatus
    confidence: float | None
    components: tuple[ReadinessComponent, ...]
    flags: tuple[str, ...]
    summary: str
    validation_level: str
    engine_version: str
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "status": self.status,
            "confidence": self.confidence,
            "components": [
                component.to_dict()
                for component in self.components
            ],
            "flags": list(self.flags),
            "summary": self.summary,
            "validation_level": self.validation_level,
            "engine_version": self.engine_version,
            "limitations": list(self.limitations),
        }
