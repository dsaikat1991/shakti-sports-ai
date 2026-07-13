from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.athlete_intelligence.models import (
    AthleteSessionProfile,
)


ADVERSE_DIRECTIONS = {
    "ground_contact_ms": "higher",
    "braking_index": "higher",
    "vertical_oscillation_percent": "higher",
    "mechanical_efficiency_score": "lower",
    "cadence_spm": "lower",
    "leg_spring_score": "lower",
    "symmetry_score": "lower",
    "sprint_economy_score": "lower",
    "max_velocity_maintenance_score": "lower",
}


def detect_fatigue_signature(
    sessions: list[AthleteSessionProfile],
    *,
    recent_window: int = 3,
) -> dict[str, Any]:
    ordered = sorted(
        sessions,
        key=lambda session: session.recorded_at,
    )

    if len(ordered) < recent_window + 2:
        return {
            "status": "insufficient_data",
            "pattern_detected": False,
        }

    baseline = ordered[
        :-recent_window
    ]

    recent = ordered[
        -recent_window:
    ]

    findings = []

    for feature_name, direction in ADVERSE_DIRECTIONS.items():
        baseline_values = [
            session.features[
                feature_name
            ]
            for session in baseline
            if feature_name
            in session.features
        ]

        recent_values = [
            session.features[
                feature_name
            ]
            for session in recent
            if feature_name
            in session.features
        ]

        if not baseline_values or not recent_values:
            continue

        baseline_mean = mean(
            baseline_values
        )

        recent_mean = mean(
            recent_values
        )

        change_percent = (
            0.0
            if abs(baseline_mean) <= 1e-12
            else (
                recent_mean
                - baseline_mean
            )
            / abs(
                baseline_mean
            )
            * 100.0
        )

        adverse = (
            change_percent >= 3.0
            if direction == "higher"
            else change_percent <= -3.0
        )

        if adverse:
            findings.append(
                {
                    "feature_name": feature_name,
                    "baseline_mean": round(
                        baseline_mean,
                        3,
                    ),
                    "recent_mean": round(
                        recent_mean,
                        3,
                    ),
                    "change_percent": round(
                        change_percent,
                        2,
                    ),
                    "adverse_direction": direction,
                }
            )

    pattern_detected = (
        len(findings) >= 3
    )

    return {
        "status": "completed",
        "pattern_detected": (
            pattern_detected
        ),
        "fatigue_signature_score": min(
            100.0,
            len(findings)
            / max(
                len(
                    ADVERSE_DIRECTIONS
                ),
                1,
            )
            * 100.0,
        ),
        "evidence_count": len(
            findings
        ),
        "findings": findings,
        "message": (
            "A multi-metric fatigue signature is present."
            if pattern_detected
            else "No strong multi-metric fatigue signature was found."
        ),
        "limitations": [
            "This is not a medical diagnosis.",
            "Training load, sleep, illness, soreness, and nutrition are not included unless supplied separately.",
        ],
        "engine_version": "0.1.0",
    }
