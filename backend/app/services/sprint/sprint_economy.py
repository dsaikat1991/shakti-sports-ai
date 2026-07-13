from __future__ import annotations

from app.services.sprint.performance_evidence import PerformanceEvidence
from app.services.sprint.sprint_pro_scoring import (
    confidence_percent,
    inverse_score,
    rating,
    weighted_score,
)


def analyze_sprint_economy(inputs: dict) -> dict:
    horizontal = weighted_score([
        (inputs.get("horizontal_force_score"), 0.40),
        (inputs.get("net_propulsion_score"), 0.40),
        (
            None if inputs.get("braking_index") is None
            else 100.0 - float(inputs["braking_index"]),
            0.20,
        ),
    ])

    vertical = weighted_score([
        (
            inverse_score(
                inputs.get("vertical_oscillation_percent"),
                ideal_max=6.0,
                poor_max=16.0,
            ),
            0.45,
        ),
        (inputs.get("leg_spring_score"), 0.35),
        (inputs.get("bounce_efficiency_score"), 0.20),
    ])

    rhythm = weighted_score([
        (
            inverse_score(
                inputs.get("cadence_cv_percent"),
                ideal_max=3.0,
                poor_max=15.0,
            ),
            0.35,
        ),
        (
            inverse_score(
                inputs.get("contact_cv_percent"),
                ideal_max=4.0,
                poor_max=18.0,
            ),
            0.35,
        ),
        (inputs.get("stride_geometry_stability_score"), 0.30),
    ])

    motion = weighted_score([
        (inputs.get("stride_geometry_score"), 0.35),
        (inputs.get("foot_trajectory_score"), 0.25),
        (horizontal, 0.25),
        (vertical, 0.15),
    ])

    waste = weighted_score([
        (
            None if inputs.get("braking_index") is None
            else float(inputs["braking_index"]),
            0.35,
        ),
        (
            None if vertical is None else 100.0 - vertical,
            0.25,
        ),
        (
            None if inputs.get("foot_trajectory_score") is None
            else 100.0 - float(inputs["foot_trajectory_score"]),
            0.20,
        ),
        (
            None if inputs.get("stride_geometry_stability_score") is None
            else 100.0 - float(inputs["stride_geometry_stability_score"]),
            0.20,
        ),
    ])

    overall = weighted_score([
        (motion, 0.25),
        (horizontal, 0.25),
        (vertical, 0.20),
        (rhythm, 0.20),
        (None if waste is None else 100.0 - waste, 0.10),
    ])

    evidence = []
    warnings = []
    if horizontal is not None and horizontal >= 80:
        evidence.append("Horizontal force transfer is efficient.")
    if vertical is not None and vertical < 60:
        warnings.append("Vertical movement leakage reduces mechanical economy.")
    if rhythm is not None and rhythm >= 80:
        evidence.append("Stride rhythm is mechanically consistent.")
    if waste is not None and waste > 35:
        warnings.append("Estimated mechanical waste is elevated.")

    result = PerformanceEvidence(
        status="experimental" if overall is not None else "insufficient_data",
        engine="sprint_economy",
        engine_version="0.1.0",
        validation_level="experimental",
        score=overall,
        confidence=confidence_percent(inputs.get("confidences", [])),
        metrics={
            "motion_efficiency_index": motion,
            "horizontal_economy_score": horizontal,
            "vertical_economy_score": vertical,
            "rhythm_economy_score": rhythm,
            "mechanical_waste_index": waste,
            "overall_sprint_economy_score": overall,
            "rating": rating(overall),
        },
        evidence=tuple(evidence),
        warnings=tuple(warnings),
        limitations=(
            "This is mechanical economy, not metabolic running economy.",
            "No VO2, oxygen cost, calories, or metabolic power are estimated.",
        ),
    )
    return result.to_dict()
