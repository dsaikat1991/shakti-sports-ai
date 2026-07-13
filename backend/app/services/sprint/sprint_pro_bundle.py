from __future__ import annotations

from app.services.sprint.sprint_intelligence_fusion import (
    fuse_sprint_intelligence,
)


def build_sprint_pro_summary(
    *,
    horizontal_force: dict | None = None,
    propulsion_braking: dict | None = None,
    stride_geometry: dict | None = None,
    foot_trajectory: dict | None = None,
    leg_spring: dict | None = None,
    sprint_economy: dict | None = None,
    arm_mechanics: dict | None = None,
    pelvis_trunk: dict | None = None,
    max_velocity_maintenance: dict | None = None,
) -> dict:
    return fuse_sprint_intelligence({
        "horizontal_force": horizontal_force or {},
        "propulsion_braking": propulsion_braking or {},
        "stride_geometry": stride_geometry or {},
        "foot_trajectory": foot_trajectory or {},
        "leg_spring": leg_spring or {},
        "sprint_economy": sprint_economy or {},
        "arm_mechanics": arm_mechanics or {},
        "pelvis_trunk": pelvis_trunk or {},
        "max_velocity_maintenance": max_velocity_maintenance or {},
    })
