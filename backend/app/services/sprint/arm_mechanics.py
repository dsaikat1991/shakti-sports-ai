from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from statistics import mean

from app.services.sprint.performance_evidence import PerformanceEvidence
from app.services.sprint.sprint_pro_scoring import (
    confidence_percent,
    cv_percent,
    inverse_score,
    rating,
    target_score,
    weighted_score,
)


@dataclass(slots=True, frozen=True)
class ArmFrame:
    frame_index: int
    timestamp_ms: int
    side: str
    phase: str
    shoulder_x: float
    shoulder_y: float
    elbow_x: float
    elbow_y: float
    wrist_x: float
    wrist_y: float
    elbow_angle_deg: float | None
    wrist_velocity_x: float | None
    wrist_velocity_y: float | None
    confidence: float


def _side_metrics(frames: list[ArmFrame], side: str, phase: str) -> dict:
    selected = sorted(
        [f for f in frames if f.side == side and f.phase == phase],
        key=lambda f: f.timestamp_ms,
    )
    if len(selected) < 4:
        return {}

    elbow_angles = [f.elbow_angle_deg for f in selected if f.elbow_angle_deg is not None]
    speeds = [
        hypot(f.wrist_velocity_x, f.wrist_velocity_y)
        for f in selected
        if f.wrist_velocity_x is not None and f.wrist_velocity_y is not None
    ]
    crossover = [
        abs(f.wrist_x - f.shoulder_x)
        for f in selected
    ]

    elbow_score = target_score(
        mean(elbow_angles) if elbow_angles else None,
        ideal_min=70.0,
        ideal_max=120.0,
        tolerance=50.0,
    )
    speed_stability = inverse_score(
        cv_percent(speeds),
        ideal_max=12.0,
        poor_max=50.0,
    )
    crossover_score = inverse_score(
        mean(crossover),
        ideal_max=0.12,
        poor_max=0.45,
    )
    score = weighted_score([
        (elbow_score, 0.35),
        (speed_stability, 0.35),
        (crossover_score, 0.30),
    ])
    return {
        "score": score,
        "average_elbow_angle_deg": round(mean(elbow_angles), 2) if elbow_angles else None,
        "peak_wrist_speed_normalized": round(max(speeds), 4) if speeds else None,
        "arm_speed_stability_score": speed_stability,
        "crossover_control_score": crossover_score,
        "confidence": confidence_percent([f.confidence for f in selected]),
    }


def analyze_arm_mechanics(frames: list[ArmFrame], *, phase: str) -> dict:
    left = _side_metrics(frames, "left", phase)
    right = _side_metrics(frames, "right", phase)

    if not left and not right:
        return PerformanceEvidence(
            status="insufficient_data",
            engine="arm_mechanics",
            engine_version="0.1.0",
            validation_level="experimental",
            score=None,
            confidence=None,
            metrics={},
        ).to_dict()

    scores = [x["score"] for x in (left, right) if x and x["score"] is not None]
    symmetry = None
    if left and right and left["score"] is not None and right["score"] is not None:
        denominator = max(left["score"], right["score"], 1e-9)
        symmetry = round((1.0 - abs(left["score"] - right["score"]) / denominator) * 100.0, 2)

    overall = weighted_score([
        (mean(scores) if scores else None, 0.75),
        (symmetry, 0.25),
    ])

    return PerformanceEvidence(
        status="experimental",
        engine="arm_mechanics",
        engine_version="0.1.0",
        validation_level="experimental",
        score=overall,
        confidence=confidence_percent([
            left.get("confidence") / 100.0 if left.get("confidence") is not None else None,
            right.get("confidence") / 100.0 if right.get("confidence") is not None else None,
        ]),
        metrics={
            "phase": phase,
            "left": left,
            "right": right,
            "arm_swing_symmetry_score": symmetry,
            "overall_arm_mechanics_score": overall,
            "rating": rating(overall),
        },
        evidence=("Arm swing is symmetrical." if symmetry is not None and symmetry >= 90 else "",),
        warnings=("Arm swing asymmetry is elevated." if symmetry is not None and symmetry < 75 else "",),
        limitations=(
            "Arm contribution is an image-space kinematic index, not joint power.",
            "Out-of-plane shoulder rotation is not recovered from a single camera.",
        ),
    ).to_dict()
