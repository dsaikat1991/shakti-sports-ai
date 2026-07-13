from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from app.services.sprint.performance_evidence import PerformanceEvidence
from app.services.sprint.sprint_pro_scoring import (
    confidence_percent,
    inverse_score,
    rating,
    weighted_score,
)


@dataclass(slots=True, frozen=True)
class VelocityFrame:
    frame_index: int
    timestamp_ms: int
    phase: str
    velocity_x: float
    cadence_spm: float | None
    ground_contact_ms: float | None
    confidence: float


def analyze_max_velocity_maintenance(frames: list[VelocityFrame]) -> dict:
    selected = sorted(
        [f for f in frames if f.phase == "maximum_velocity"],
        key=lambda f: f.timestamp_ms,
    )
    if len(selected) < 5:
        return PerformanceEvidence(
            status="insufficient_data",
            engine="max_velocity_maintenance",
            engine_version="0.1.0",
            validation_level="experimental",
            score=None,
            confidence=None,
            metrics={},
        ).to_dict()

    velocities = [abs(f.velocity_x) for f in selected]
    peak = max(velocities)
    peak_index = velocities.index(peak)
    tail = velocities[peak_index:] or [peak]
    final = tail[-1]
    drop_percent = 0.0 if peak <= 1e-12 else max(0.0, (peak - final) / peak * 100.0)

    maintained = [v for v in velocities if v >= peak * 0.95]
    duration_ms = 0
    if len(maintained) >= 2:
        first_i = next(i for i, v in enumerate(velocities) if v >= peak * 0.95)
        last_i = len(velocities) - 1 - next(
            i for i, v in enumerate(reversed(velocities)) if v >= peak * 0.95
        )
        duration_ms = selected[last_i].timestamp_ms - selected[first_i].timestamp_ms

    cadence_values = [f.cadence_spm for f in selected if f.cadence_spm is not None]
    contact_values = [f.ground_contact_ms for f in selected if f.ground_contact_ms is not None]

    retention_score = inverse_score(drop_percent, ideal_max=3.0, poor_max=15.0)
    duration_score = min(100.0, duration_ms / 2000.0 * 100.0)
    cadence_stability = inverse_score(
        0.0 if len(cadence_values) < 2 else (
            max(cadence_values) - min(cadence_values)
        ) / max(mean(cadence_values), 1e-9) * 100.0,
        ideal_max=3.0,
        poor_max=15.0,
    )
    contact_stability = inverse_score(
        0.0 if len(contact_values) < 2 else (
            max(contact_values) - min(contact_values)
        ) / max(mean(contact_values), 1e-9) * 100.0,
        ideal_max=4.0,
        poor_max=18.0,
    )

    overall = weighted_score([
        (retention_score, 0.45),
        (duration_score, 0.25),
        (cadence_stability, 0.15),
        (contact_stability, 0.15),
    ])

    return PerformanceEvidence(
        status="experimental",
        engine="max_velocity_maintenance",
        engine_version="0.1.0",
        validation_level="experimental",
        score=overall,
        confidence=confidence_percent([f.confidence for f in selected]),
        metrics={
            "peak_velocity": round(peak, 6),
            "final_velocity": round(final, 6),
            "velocity_drop_percent": round(drop_percent, 2),
            "velocity_95_percent_maintenance_ms": int(duration_ms),
            "velocity_retention_score": retention_score,
            "cadence_stability_score": cadence_stability,
            "contact_stability_score": contact_stability,
            "overall_max_velocity_maintenance_score": overall,
            "rating": rating(overall),
        },
        evidence=(
            "Velocity is maintained efficiently."
            if retention_score is not None and retention_score >= 80
            else "",
        ),
        warnings=(
            "Velocity declines substantially after peak speed."
            if drop_percent > 10
            else "",
        ),
        limitations=(
            "Velocity is camera-relative unless a calibrated scale is supplied upstream.",
            "Maintenance duration depends on the analysed clip containing a true maximum-velocity segment.",
        ),
    ).to_dict()
