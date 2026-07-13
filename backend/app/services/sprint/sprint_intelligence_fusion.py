from __future__ import annotations

from app.services.sprint.performance_evidence import PerformanceEvidence
from app.services.sprint.sprint_pro_scoring import (
    confidence_percent,
    rating,
    weighted_score,
)


ENGINE_WEIGHTS = {
    "horizontal_force": 0.14,
    "propulsion_braking": 0.14,
    "stride_geometry": 0.12,
    "foot_trajectory": 0.10,
    "leg_spring": 0.12,
    "sprint_economy": 0.16,
    "arm_mechanics": 0.07,
    "pelvis_trunk": 0.08,
    "max_velocity_maintenance": 0.07,
}


def fuse_sprint_intelligence(engine_results: dict[str, dict]) -> dict:
    weighted = []
    confidences = []
    contributions = []

    for engine_name, weight in ENGINE_WEIGHTS.items():
        result = engine_results.get(engine_name, {})
        score = result.get("score")
        confidence = result.get("confidence")

        weighted.append((score, weight))
        if confidence is not None:
            confidences.append(float(confidence) / 100.0)

        contributions.append({
            "engine": engine_name,
            "score": score,
            "weight": weight,
            "confidence": confidence,
            "available": score is not None,
        })

    overall = weighted_score(weighted)

    ranked = sorted(
        [item for item in contributions if item["score"] is not None],
        key=lambda item: item["score"],
        reverse=True,
    )

    strengths = ranked[:3]
    development = sorted(
        ranked,
        key=lambda item: item["score"],
    )[:3]

    evidence = tuple(
        f"{item['engine']} is a leading strength."
        for item in strengths
        if item["score"] >= 80
    )
    warnings = tuple(
        f"{item['engine']} is a priority development area."
        for item in development
        if item["score"] < 70
    )

    return PerformanceEvidence(
        status="experimental" if overall is not None else "insufficient_data",
        engine="sprint_intelligence_fusion",
        engine_version="0.1.0",
        validation_level="experimental",
        score=overall,
        confidence=confidence_percent(confidences),
        metrics={
            "overall_sprint_intelligence_score": overall,
            "rating": rating(overall),
            "engine_contributions": contributions,
            "top_strengths": strengths,
            "priority_development_areas": development,
            "engines_available": sum(1 for item in contributions if item["available"]),
            "engines_expected": len(ENGINE_WEIGHTS),
        },
        evidence=evidence,
        warnings=warnings,
        limitations=(
            "Fusion weights are provisional and require calibration against sprint outcomes.",
            "The score is not a prediction of race time or long-term potential.",
            "Missing engine outputs are excluded and remaining weights are renormalized.",
        ),
    ).to_dict()
