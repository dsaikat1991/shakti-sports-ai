from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.coach.models import (
    CoachingInsight,
    MetricEvidence,
)
from app.services.coach.rules import (
    CoachRule,
    DEFAULT_RULES,
)


def _metric_confidence(
    confidences: dict[str, float],
    names: tuple[str, ...],
) -> float | None:
    values = [
        max(
            0.0,
            min(
                1.0,
                float(
                    confidences[name]
                ),
            ),
        )
        for name in names
        if name in confidences
        and isinstance(
            confidences[name],
            (int, float),
        )
    ]

    if not values:
        return None

    return round(
        mean(values),
        4,
    )


def _comparison_text(
    value: float | None,
) -> str:
    if value is None:
        return "available"

    return "observed"


def _build_evidence(
    rule: CoachRule,
    metrics: dict[str, Any],
    confidences: dict[str, float],
    units: dict[str, str],
) -> tuple[MetricEvidence, ...]:
    evidence: list[
        MetricEvidence
    ] = []

    for metric_name in rule.evidence_metrics:
        value = metrics.get(
            metric_name
        )

        numeric_value = (
            float(value)
            if isinstance(
                value,
                (int, float),
            )
            else None
        )

        evidence.append(
            MetricEvidence(
                metric_name=metric_name,
                value=numeric_value,
                unit=units.get(
                    metric_name
                ),
                confidence=confidences.get(
                    metric_name
                ),
                comparison=_comparison_text(
                    numeric_value
                ),
                threshold=None,
                message=(
                    f"{metric_name} was used as evidence "
                    f"for rule {rule.rule_id}."
                ),
            )
        )

    return tuple(evidence)


def evaluate_coach_rules(
    *,
    metrics: dict[str, Any],
    confidences: dict[str, float] | None = None,
    units: dict[str, str] | None = None,
    rules: tuple[CoachRule, ...] = DEFAULT_RULES,
) -> list[CoachingInsight]:
    active_confidences = (
        confidences
        or {}
    )

    active_units = (
        units
        or {}
    )

    insights: list[
        CoachingInsight
    ] = []

    for rule in rules:
        try:
            matched = bool(
                rule.condition(
                    metrics
                )
            )
        except (
            TypeError,
            ValueError,
            KeyError,
        ):
            matched = False

        if not matched:
            continue

        confidence = _metric_confidence(
            active_confidences,
            rule.evidence_metrics,
        )

        insights.append(
            CoachingInsight(
                rule_id=rule.rule_id,
                title=rule.title,
                category=rule.category,
                priority=rule.priority,
                summary=rule.summary,
                likely_causes=(
                    rule.likely_causes
                ),
                recommendations=(
                    rule.recommendations
                ),
                evidence=_build_evidence(
                    rule,
                    metrics,
                    active_confidences,
                    active_units,
                ),
                confidence=(
                    round(
                        confidence
                        * 100.0,
                        2,
                    )
                    if confidence
                    is not None
                    else None
                ),
                validation_level=(
                    rule.validation_level
                ),
                version=rule.version,
            )
        )

    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    insights.sort(
        key=lambda item: (
            priority_order[
                item.priority
            ],
            item.rule_id,
        )
    )

    return insights
