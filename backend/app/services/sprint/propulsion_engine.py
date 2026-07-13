from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.sprint.propulsion_models import (
    ContactMotionFrame,
    ContactPhaseMetrics,
)
from app.services.sprint.propulsion_scoring import (
    braking_index_from_areas,
    confidence_percent,
    integrate_trapezoid,
    net_propulsion_score,
    propulsion_score_from_areas,
    quality_label,
)


SUPPORTED_PHASES = {
    "drive",
    "transition",
    "maximum_velocity",
}


def _foot_offset_percent(
    frame: ContactMotionFrame,
) -> float:
    return (
        frame.foot_x
        - frame.com_x
    ) * 100.0


def _shin_alignment_score(
    frame: ContactMotionFrame,
) -> float | None:
    if frame.shin_angle_deg is None:
        return None

    target_ranges = {
        "drive": (45.0, 70.0),
        "transition": (55.0, 78.0),
        "maximum_velocity": (65.0, 88.0),
    }

    low, high = target_ranges.get(
        frame.phase,
        (55.0, 85.0),
    )

    if low <= frame.shin_angle_deg <= high:
        return 100.0

    distance = (
        low - frame.shin_angle_deg
        if frame.shin_angle_deg < low
        else frame.shin_angle_deg - high
    )

    return round(
        max(
            0.0,
            100.0
            * (
                1.0 - distance / 30.0
            ),
        ),
        2,
    )


def analyze_propulsion_braking(
    frames: list[ContactMotionFrame],
    *,
    side: str,
    phase: str,
) -> dict[str, Any]:
    if phase not in SUPPORTED_PHASES:
        return {
            "status": "unsupported_phase",
            "metrics": None,
        }

    selected = sorted(
        [
            frame
            for frame in frames
            if frame.side == side
            and frame.phase == phase
            and frame.contact_probability >= 0.50
        ],
        key=lambda frame: frame.timestamp_ms,
    )

    if len(selected) < 4:
        return {
            "status": "insufficient_data",
            "metrics": None,
        }

    timestamps = [
        frame.timestamp_ms
        for frame in selected
    ]

    negative_acceleration = [
        min(
            0.0,
            frame.com_acceleration_x,
        )
        for frame in selected
    ]

    positive_acceleration = [
        max(
            0.0,
            frame.com_acceleration_x,
        )
        for frame in selected
    ]

    braking_area = integrate_trapezoid(
        timestamps,
        negative_acceleration,
    )

    propulsive_area = integrate_trapezoid(
        timestamps,
        positive_acceleration,
    )

    braking_frames = [
        frame
        for frame in selected
        if frame.com_acceleration_x < 0.0
    ]

    propulsion_frames = [
        frame
        for frame in selected
        if frame.com_acceleration_x > 0.0
    ]

    braking_duration = (
        braking_frames[-1].timestamp_ms
        - braking_frames[0].timestamp_ms
        if len(braking_frames) >= 2
        else 0.0
    )

    propulsive_duration = (
        propulsion_frames[-1].timestamp_ms
        - propulsion_frames[0].timestamp_ms
        if len(propulsion_frames) >= 2
        else 0.0
    )

    braking_index = braking_index_from_areas(
        braking_area=braking_area,
        propulsive_area=propulsive_area,
    )

    propulsion_score = propulsion_score_from_areas(
        braking_area=braking_area,
        propulsive_area=propulsive_area,
    )

    offsets = [
        _foot_offset_percent(
            frame
        )
        for frame in selected
    ]

    average_offset = mean(
        offsets
    )

    shin_scores = [
        score
        for score in (
            _shin_alignment_score(
                frame
            )
            for frame in selected
        )
        if score is not None
    ]

    average_shin_score = (
        mean(shin_scores)
        if shin_scores
        else None
    )

    net_score = net_propulsion_score(
        braking_index=braking_index,
        propulsion_score=propulsion_score,
        foot_offset_percent=average_offset,
        shin_alignment_score=average_shin_score,
    )

    confidence = confidence_percent(
        [
            frame.confidence
            for frame in selected
        ]
    )

    metrics = ContactPhaseMetrics(
        side=side,
        phase=phase,
        frames_used=len(selected),
        braking_duration_ms=round(
            braking_duration,
            2,
        ),
        propulsive_duration_ms=round(
            propulsive_duration,
            2,
        ),
        braking_acceleration_area=round(
            braking_area,
            6,
        ),
        propulsive_acceleration_area=round(
            propulsive_area,
            6,
        ),
        braking_index=braking_index,
        propulsion_effectiveness_score=(
            propulsion_score
        ),
        net_horizontal_propulsion_score=(
            net_score
        ),
        contact_direction_quality=quality_label(
            net_score
        ),
        confidence=confidence,
    )

    evidence: list[str] = []
    warnings: list[str] = []

    if braking_index <= 20.0:
        evidence.append(
            "Braking contribution is low relative to propulsion."
        )
    elif braking_index >= 40.0:
        warnings.append(
            "A large share of contact motion is associated with braking."
        )

    if propulsion_score >= 75.0:
        evidence.append(
            "Positive horizontal acceleration dominates the contact phase."
        )
    elif propulsion_score < 55.0:
        warnings.append(
            "Propulsive contribution is limited."
        )

    if average_offset <= 10.0:
        evidence.append(
            "Foot placement is close to the centre of mass."
        )
    elif average_offset > 20.0:
        warnings.append(
            "Foot placement ahead of the centre of mass may increase braking."
        )

    return {
        "status": "experimental",
        "metrics": metrics.to_dict(),
        "evidence": evidence,
        "warnings": warnings,
        "supporting_measurements": {
            "average_foot_offset_from_com_percent": round(
                average_offset,
                2,
            ),
            "average_shin_alignment_score": (
                round(
                    average_shin_score,
                    2,
                )
                if average_shin_score
                is not None
                else None
            ),
        },
        "method": (
            "contact_phase_acceleration_balance_v0.1"
        ),
        "validation_level": "experimental",
        "engine_version": "0.1.0",
        "limitations": [
            "Acceleration areas are camera-relative motion proxies, not force-plate impulses.",
            "The engine does not report Newton-seconds or absolute force.",
            "Contact segmentation quality directly affects braking and propulsion estimates.",
            "Thresholds require validation against instrumented sprint data.",
        ],
    }


def analyze_propulsion_braking_by_phase(
    frames: list[ContactMotionFrame],
) -> dict[str, Any]:
    results: dict[
        str,
        dict[str, Any],
    ] = {}

    scores: list[float] = []

    for side in (
        "left",
        "right",
    ):
        results[side] = {}

        for phase in (
            "drive",
            "transition",
            "maximum_velocity",
        ):
            result = analyze_propulsion_braking(
                frames,
                side=side,
                phase=phase,
            )

            results[side][phase] = result

            if (
                result["status"]
                == "experimental"
                and result["metrics"][
                    "net_horizontal_propulsion_score"
                ]
                is not None
            ):
                scores.append(
                    result["metrics"][
                        "net_horizontal_propulsion_score"
                    ]
                )

    return {
        "status": (
            "completed"
            if scores
            else "insufficient_data"
        ),
        "sides": results,
        "overall_average_net_propulsion_score": (
            round(
                mean(scores),
                2,
            )
            if scores
            else None
        ),
        "engine_version": "0.1.0",
    }
