from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.athlete_intelligence.models import (
    AthleteFingerprint,
    AthleteSessionProfile,
)
from app.services.athlete_intelligence.scoring import (
    confidence_percent,
)


FINGERPRINT_FEATURES = (
    "mechanical_efficiency_score",
    "horizontal_force_score",
    "net_propulsion_score",
    "stride_geometry_score",
    "foot_trajectory_score",
    "leg_spring_score",
    "sprint_economy_score",
    "arm_mechanics_score",
    "pelvis_trunk_score",
    "max_velocity_maintenance_score",
    "symmetry_score",
)


def build_biomechanical_fingerprint(
    sessions: list[AthleteSessionProfile],
) -> dict[str, Any]:
    if not sessions:
        return {
            "status": "insufficient_data",
            "fingerprint": None,
        }

    ordered = sorted(
        sessions,
        key=lambda session: session.recorded_at,
    )

    vector: dict[str, float] = {}
    confidence_values: list[float | None] = []

    for feature_name in FINGERPRINT_FEATURES:
        values = [
            session.features[
                feature_name
            ]
            for session in ordered
            if feature_name
            in session.features
        ]

        if not values:
            continue

        vector[
            feature_name
        ] = round(
            mean(values),
            4,
        )

        for session in ordered:
            if (
                session.confidences
                and feature_name
                in session.confidences
            ):
                confidence_values.append(
                    session.confidences[
                        feature_name
                    ]
                )

    if not vector:
        return {
            "status": "insufficient_data",
            "fingerprint": None,
        }

    dominant_traits = tuple(
        feature_name
        for feature_name, _
        in sorted(
            vector.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:4]
    )

    fingerprint = AthleteFingerprint(
        athlete_id=ordered[-1].athlete_id,
        event=ordered[-1].event,
        vector=vector,
        dominant_traits=dominant_traits,
        confidence=confidence_percent(
            confidence_values
        ),
    )

    return {
        "status": "completed",
        "fingerprint": (
            fingerprint.to_dict()
        ),
    }
