from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class PerformanceEvidence:
    status: str
    engine: str
    engine_version: str
    validation_level: str
    score: float | None
    confidence: float | None
    metrics: dict[str, Any]
    evidence: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["evidence"] = list(self.evidence)
        result["warnings"] = list(self.warnings)
        result["limitations"] = list(self.limitations)
        return result
