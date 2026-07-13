from __future__ import annotations

from dataclasses import dataclass
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
class PelvisTrunkFrame:
    frame_index: int
    timestamp_ms: int
    phase: str
    left_shoulder_y: float
    right_shoulder_y: float
    left_hip_y: float
    right_hip_y: float
    shoulder_width: float
    hip_width: float
    trunk_angle_deg: float | None
    head_x: float | None
    head_y: float | None
    com_x: float
    com_y: float
    confidence: float


def analyze_pelvis_trunk(frames: list[PelvisTrunkFrame], *, phase: str) -> dict:
    selected = sorted(
        [f for f in frames if f.phase == phase],
        key=lambda f: f.timestamp_ms,
    )
    if len(selected) < 5:
        return PerformanceEvidence(
            status="insufficient_data",
            engine="pelvis_trunk",
            engine_version="0.1.0",
            validation_level="experimental",
            score=None,
            confidence=None,
            metrics={},
        ).to_dict()

    pelvic_tilt = [
        abs(f.left_hip_y - f.right_hip_y) / max(f.hip_width, 1e-6) * 100.0
        for f in selected
    ]
    shoulder_tilt = [
        abs(f.left_shoulder_y - f.right_shoulder_y) / max(f.shoulder_width, 1e-6) * 100.0
        for f in selected
    ]
    trunk_angles = [f.trunk_angle_deg for f in selected if f.trunk_angle_deg is not None]
    head_offsets = [
        abs(f.head_x - f.com_x)
        for f in selected
        if f.head_x is not None
    ]

    pelvis_stability = inverse_score(
        cv_percent(pelvic_tilt),
        ideal_max=10.0,
        poor_max=45.0,
    )
    trunk_stability = inverse_score(
        cv_percent(trunk_angles),
        ideal_max=4.0,
        poor_max=20.0,
    )
    head_stability = inverse_score(
        cv_percent(head_offsets),
        ideal_max=12.0,
        poor_max=55.0,
    )
    shoulder_hip_separation = abs(
        mean(shoulder_tilt) - mean(pelvic_tilt)
    )
    separation_score = target_score(
        shoulder_hip_separation,
        ideal_min=0.0,
        ideal_max=8.0,
        tolerance=25.0,
    )

    overall = weighted_score([
        (pelvis_stability, 0.30),
        (trunk_stability, 0.30),
        (head_stability, 0.20),
        (separation_score, 0.20),
    ])

    evidence = []
    warnings = []
    if pelvis_stability is not None and pelvis_stability >= 80:
        evidence.append("Pelvic control is stable.")
    if trunk_stability is not None and trunk_stability < 60:
        warnings.append("Trunk-angle variability is elevated.")
    if head_stability is not None and head_stability < 60:
        warnings.append("Head position is unstable relative to the COM.")

    return PerformanceEvidence(
        status="experimental",
        engine="pelvis_trunk",
        engine_version="0.1.0",
        validation_level="experimental",
        score=overall,
        confidence=confidence_percent([f.confidence for f in selected]),
        metrics={
            "phase": phase,
            "average_pelvic_tilt_percent": round(mean(pelvic_tilt), 2),
            "average_shoulder_tilt_percent": round(mean(shoulder_tilt), 2),
            "pelvis_stability_score": pelvis_stability,
            "trunk_stability_score": trunk_stability,
            "head_stability_score": head_stability,
            "shoulder_hip_separation_score": separation_score,
            "overall_pelvis_trunk_score": overall,
            "rating": rating(overall),
        },
        evidence=tuple(evidence),
        warnings=tuple(warnings),
        limitations=(
            "Pelvic rotation and shoulder-hip separation are 2D image-plane proxies.",
            "True transverse-plane rotation requires calibrated 3D analysis.",
        ),
    ).to_dict()
