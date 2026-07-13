from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.coach.evaluator import (
    evaluate_coach_rules,
)
from app.services.coach.models import (
    CoachReport,
    CoachingInsight,
)


def _unique_training_focus(
    insights: list[CoachingInsight],
    *,
    maximum_items: int = 8,
) -> tuple[str, ...]:
    focus: list[str] = []

    for insight in insights:
        for recommendation in insight.recommendations:
            if recommendation in focus:
                continue

            focus.append(
                recommendation
            )

            if len(focus) >= maximum_items:
                return tuple(focus)

    return tuple(focus)


def _overall_confidence(
    insights: list[CoachingInsight],
) -> float | None:
    values = [
        insight.confidence
        for insight in insights
        if insight.confidence is not None
    ]

    if not values:
        return None

    return round(
        mean(values),
        2,
    )


def _executive_summary(
    strengths: list[CoachingInsight],
    development: list[CoachingInsight],
) -> str:
    if not strengths and not development:
        return (
            "No deterministic coaching rule was triggered "
            "from the available metrics."
        )

    if development:
        highest = development[0]

        if strengths:
            return (
                f"The main development priority is "
                f"{highest.title.lower()}. "
                f"A current strength is "
                f"{strengths[0].title.lower()}."
            )

        return (
            f"The main development priority is "
            f"{highest.title.lower()}."
        )

    return (
        f"The strongest detected pattern is "
        f"{strengths[0].title.lower()}."
    )


def build_coach_report(
    *,
    metrics: dict[str, Any],
    confidences: dict[str, float] | None = None,
    units: dict[str, str] | None = None,
) -> dict[str, Any]:
    insights = evaluate_coach_rules(
        metrics=metrics,
        confidences=confidences,
        units=units,
    )

    strengths = [
        insight
        for insight in insights
        if insight.priority == "low"
    ]

    development = [
        insight
        for insight in insights
        if insight.priority
        in (
            "critical",
            "high",
            "medium",
        )
    ]

    report = CoachReport(
        status=(
            "completed"
            if insights
            else "insufficient_evidence"
        ),
        executive_summary=(
            _executive_summary(
                strengths,
                development,
            )
        ),
        strengths=tuple(
            strengths
        ),
        development_priorities=tuple(
            development
        ),
        training_focus=(
            _unique_training_focus(
                development
                if development
                else strengths
            )
        ),
        confidence=(
            _overall_confidence(
                insights
            )
        ),
        validation_level="experimental",
        engine_version="0.1.0",
        limitations=(
            "Rules use provisional thresholds and must be validated with qualified sprint coaches.",
            "Recommendations are training suggestions, not medical advice.",
            "The engine only reasons from metrics explicitly supplied to it.",
            "An LLM should only rewrite this structured output and must not add new conclusions.",
        ),
    )

    return report.to_dict()
