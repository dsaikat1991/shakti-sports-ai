from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


Condition = Callable[
    [dict[str, Any]],
    bool,
]


@dataclass(slots=True, frozen=True)
class CoachRule:
    rule_id: str
    title: str
    category: str
    priority: str
    condition: Condition
    summary: str
    likely_causes: tuple[str, ...]
    recommendations: tuple[str, ...]
    evidence_metrics: tuple[str, ...]
    validation_level: str = "experimental"
    version: str = "0.1.0"


def _number(
    metrics: dict[str, Any],
    name: str,
) -> float | None:
    value = metrics.get(name)

    if isinstance(value, (int, float)):
        return float(value)

    return None


def _gt(
    metrics: dict[str, Any],
    name: str,
    threshold: float,
) -> bool:
    value = _number(
        metrics,
        name,
    )

    return (
        value is not None
        and value > threshold
    )


def _lt(
    metrics: dict[str, Any],
    name: str,
    threshold: float,
) -> bool:
    value = _number(
        metrics,
        name,
    )

    return (
        value is not None
        and value < threshold
    )


DEFAULT_RULES: tuple[
    CoachRule,
    ...
] = (
    CoachRule(
        rule_id="sprint.long_contact_incomplete_push_off",
        title="Late-stance force application needs attention",
        category="force_application",
        priority="high",
        condition=lambda metrics: (
            _gt(
                metrics,
                "ground_contact_ms",
                135.0,
            )
            and _lt(
                metrics,
                "push_off_completion_score",
                65.0,
            )
        ),
        summary=(
            "Ground-contact time is prolonged and push-off "
            "completion is limited."
        ),
        likely_causes=(
            "Reduced lower-limb stiffness.",
            "Delayed hip extension.",
            "Incomplete force application before toe-off.",
        ),
        recommendations=(
            "Low-volume pogo jumps.",
            "Resisted acceleration sprints.",
            "Wall drills focused on full hip extension.",
            "Short hill sprints with complete push-off.",
        ),
        evidence_metrics=(
            "ground_contact_ms",
            "push_off_completion_score",
            "hip_extension_deg",
        ),
    ),
    CoachRule(
        rule_id="sprint.front_side_overstride",
        title="Foot strike is too far ahead of the COM",
        category="front_side_mechanics",
        priority="high",
        condition=lambda metrics: (
            _gt(
                metrics,
                "foot_offset_percent",
                20.0,
            )
        ),
        summary=(
            "The foot is landing substantially ahead of the "
            "centre of mass, increasing braking risk."
        ),
        likely_causes=(
            "Delayed downward foot preparation.",
            "Insufficient front-side recovery timing.",
            "Attempting to reach for stride length.",
        ),
        recommendations=(
            "Wicket runs at controlled spacing.",
            "Fast-leg drills with strike-down emphasis.",
            "A-runs focusing on contact beneath the hips.",
        ),
        evidence_metrics=(
            "foot_offset_percent",
            "front_side_score",
            "recovery_velocity_dps",
        ),
    ),
    CoachRule(
        rule_id="sprint.low_knee_recovery",
        title="Knee recovery is limited",
        category="front_side_mechanics",
        priority="medium",
        condition=lambda metrics: (
            _lt(
                metrics,
                "knee_lift_percent",
                28.0,
            )
            and _lt(
                metrics,
                "recovery_velocity_dps",
                550.0,
            )
        ),
        summary=(
            "Knee lift and recovery velocity are both below "
            "the provisional target range."
        ),
        likely_causes=(
            "Slow heel recovery.",
            "Limited hip-flexor contribution.",
            "Excessive back-side mechanics.",
        ),
        recommendations=(
            "A-skip and A-run progressions.",
            "Fast-leg exchange drills.",
            "Short assisted cadence drills under supervision.",
        ),
        evidence_metrics=(
            "knee_lift_percent",
            "recovery_velocity_dps",
            "back_side_duration_ms",
        ),
    ),
    CoachRule(
        rule_id="sprint.excessive_back_side",
        title="Rear-leg mechanics are excessive",
        category="back_side_mechanics",
        priority="high",
        condition=lambda metrics: (
            _gt(
                metrics,
                "trailing_distance_percent",
                30.0,
            )
            or _gt(
                metrics,
                "back_side_duration_ms",
                260.0,
            )
        ),
        summary=(
            "The leg remains behind the centre of mass for too "
            "long, which may limit cadence and recovery."
        ),
        likely_causes=(
            "Delayed heel recovery.",
            "Overemphasis on pushing behind the body.",
            "Incomplete transition into front-side mechanics.",
        ),
        recommendations=(
            "Wicket runs with compact recovery.",
            "Dribbles progressing from ankle to knee height.",
            "Fast-leg cycling drills.",
        ),
        evidence_metrics=(
            "trailing_distance_percent",
            "back_side_duration_ms",
            "heel_recovery_speed",
        ),
    ),
    CoachRule(
        rule_id="sprint.rhythm_inconsistency",
        title="Sprint rhythm is inconsistent",
        category="rhythm",
        priority="medium",
        condition=lambda metrics: (
            _gt(
                metrics,
                "cadence_cv_percent",
                10.0,
            )
            or _gt(
                metrics,
                "contact_cv_percent",
                12.0,
            )
        ),
        summary=(
            "Step rhythm or contact timing varies considerably "
            "across the analysed cycles."
        ),
        likely_causes=(
            "Fatigue.",
            "Inconsistent force application.",
            "Unstable transition between sprint phases.",
        ),
        recommendations=(
            "Submaximal rhythm runs.",
            "Wicket runs with consistent spacing.",
            "Short technical repetitions with full recovery.",
        ),
        evidence_metrics=(
            "cadence_cv_percent",
            "contact_cv_percent",
            "flight_cv_percent",
        ),
    ),
    CoachRule(
        rule_id="sprint.excessive_vertical_oscillation",
        title="Vertical motion is reducing forward efficiency",
        category="stability",
        priority="medium",
        condition=lambda metrics: (
            _gt(
                metrics,
                "vertical_oscillation_percent",
                12.0,
            )
        ),
        summary=(
            "The centre of mass is oscillating vertically more "
            "than the provisional target range."
        ),
        likely_causes=(
            "Excessive vertical force orientation.",
            "Limited pelvis control.",
            "Inconsistent contact mechanics.",
        ),
        recommendations=(
            "Straight-leg bounds with forward projection.",
            "Core and pelvis-control drills.",
            "Technical runs focusing on horizontal displacement.",
        ),
        evidence_metrics=(
            "vertical_oscillation_percent",
            "pelvis_stability_score",
            "ground_contact_ms",
        ),
    ),
    CoachRule(
        rule_id="sprint.high_mechanical_efficiency",
        title="Mechanical efficiency is a current strength",
        category="overall",
        priority="low",
        condition=lambda metrics: (
            _gt(
                metrics,
                "mechanical_efficiency_score",
                84.99,
            )
        ),
        summary=(
            "The athlete demonstrates strong overall mechanical "
            "efficiency across the available pillars."
        ),
        likely_causes=(
            "Balanced front- and back-side mechanics.",
            "Stable rhythm.",
            "Efficient force application.",
        ),
        recommendations=(
            "Maintain technical quality under progressively higher intensity.",
            "Use small targeted changes rather than major mechanical alterations.",
        ),
        evidence_metrics=(
            "mechanical_efficiency_score",
            "front_side_score",
            "back_side_score",
            "symmetry_score",
        ),
    ),
)
