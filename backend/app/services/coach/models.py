from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


Priority = Literal[
    "low",
    "medium",
    "high",
    "critical",
]


@dataclass(slots=True, frozen=True)
class MetricEvidence:
    metric_name: str
    value: float | None
    unit: str | None
    confidence: float | None
    comparison: str
    threshold: float | None
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class CoachingInsight:
    rule_id: str
    title: str
    category: str
    priority: Priority
    summary: str
    likely_causes: tuple[str, ...]
    recommendations: tuple[str, ...]
    evidence: tuple[MetricEvidence, ...]
    confidence: float | None
    validation_level: str
    version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "category": self.category,
            "priority": self.priority,
            "summary": self.summary,
            "likely_causes": list(
                self.likely_causes
            ),
            "recommendations": list(
                self.recommendations
            ),
            "evidence": [
                item.to_dict()
                for item in self.evidence
            ],
            "confidence": self.confidence,
            "validation_level": (
                self.validation_level
            ),
            "version": self.version,
        }


@dataclass(slots=True, frozen=True)
class CoachReport:
    status: str
    executive_summary: str
    strengths: tuple[CoachingInsight, ...]
    development_priorities: tuple[CoachingInsight, ...]
    training_focus: tuple[str, ...]
    confidence: float | None
    validation_level: str
    engine_version: str
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "executive_summary": (
                self.executive_summary
            ),
            "strengths": [
                item.to_dict()
                for item in self.strengths
            ],
            "development_priorities": [
                item.to_dict()
                for item in self.development_priorities
            ],
            "training_focus": list(
                self.training_focus
            ),
            "confidence": self.confidence,
            "validation_level": (
                self.validation_level
            ),
            "engine_version": (
                self.engine_version
            ),
            "limitations": list(
                self.limitations
            ),
        }
