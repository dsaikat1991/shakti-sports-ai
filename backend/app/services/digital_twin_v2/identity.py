from __future__ import annotations

from statistics import mean
from typing import Any

from app.services.digital_twin_v2.models import (
    TwinSession,
)


IDENTITY_FEATURES = (
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


def build_personal_identity_vector(
    sessions: list[TwinSession],
    *,
    recent_window: int = 8,
) -> dict[str, Any]:
    ordered = sorted(
        sessions,
        key=lambda item: item.recorded_at,
    )[
        -recent_window:
    ]

    vector = {}

    for feature_name in IDENTITY_FEATURES:
        values = [
            session.features[
                feature_name
            ]
            for session in ordered
            if feature_name
            in session.features
        ]

        if values:
            vector[
                feature_name
            ] = round(
                mean(values),
                4,
            )

    return {
        "status": (
            "completed"
            if vector
            else "insufficient_data"
        ),
        "vector": vector,
        "sessions_used": len(
            ordered
        ),
        "engine_version": "1.0.0",
    }
