from __future__ import annotations

from typing import Any

from app.services.digital_twin.models import (
    AthleteMetricSnapshot,
)


def detect_longitudinal_fatigue_pattern(
    snapshots: list[AthleteMetricSnapshot],
    *,
    recent_window: int = 3,
) -> dict[str, Any]:
    ordered = sorted(
        snapshots,
        key=lambda item: item.recorded_at,
    )

    if len(ordered) < recent_window + 1:
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

    tracked = {
        "ground_contact_ms": "higher",
        "cadence_spm": "lower",
        "push_off_completion_score": "lower",
        "symmetry_score": "lower",
        "mechanical_efficiency_score": "lower",
    }

    findings: list[
        dict[str, Any]
    ] = []

    for metric_name, adverse_direction in tracked.items():
        baseline_values = [
            snapshot.metrics[
                metric_name
            ]
            for snapshot in baseline
            if metric_name
            in snapshot.metrics
        ]

        recent_values = [
            snapshot.metrics[
                metric_name
            ]
            for snapshot in recent
            if metric_name
            in snapshot.metrics
        ]

        if not baseline_values or not recent_values:
            continue

        baseline_mean = sum(
            baseline_values
        ) / len(
            baseline_values
        )

        recent_mean = sum(
            recent_values
        ) / len(
            recent_values
        )

        adverse = (
            recent_mean
            > baseline_mean
            * 1.03
            if adverse_direction
            == "higher"
            else recent_mean
            < baseline_mean
            * 0.97
        )

        if adverse:
            findings.append(
                {
                    "metric_name": metric_name,
                    "baseline_mean": round(
                        baseline_mean,
                        3,
                    ),
                    "recent_mean": round(
                        recent_mean,
                        3,
                    ),
                    "adverse_direction": (
                        adverse_direction
                    ),
                }
            )

    pattern_detected = (
        len(findings) >= 2
    )

    return {
        "status": "completed",
        "pattern_detected": (
            pattern_detected
        ),
        "evidence_count": len(
            findings
        ),
        "findings": findings,
        "message": (
            "Recent multi-metric changes may be consistent with accumulated fatigue and should be reviewed by a qualified coach."
            if pattern_detected
            else "No multi-metric fatigue pattern was detected."
        ),
        "limitations": [
            "This is not a medical diagnosis.",
            "Training load, illness, sleep, and competition context are not included unless separately supplied.",
        ],
    }
