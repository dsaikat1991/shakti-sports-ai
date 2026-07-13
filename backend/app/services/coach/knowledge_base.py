from __future__ import annotations

from typing import Any

from app.services.coach.rules import (
    DEFAULT_RULES,
)


def export_knowledge_base(
) -> dict[str, Any]:
    return {
        "version": "0.1.0",
        "sport": "athletics",
        "event": "sprint",
        "rules": [
            {
                "rule_id": rule.rule_id,
                "title": rule.title,
                "category": rule.category,
                "priority": rule.priority,
                "summary": rule.summary,
                "likely_causes": list(
                    rule.likely_causes
                ),
                "recommendations": list(
                    rule.recommendations
                ),
                "evidence_metrics": list(
                    rule.evidence_metrics
                ),
                "validation_level": (
                    rule.validation_level
                ),
                "version": rule.version,
            }
            for rule in DEFAULT_RULES
        ],
    }
