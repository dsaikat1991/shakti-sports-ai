from __future__ import annotations

from dataclasses import asdict, dataclass

from app.services.pose.landmark_usability import (
    LandmarkUsabilityPolicy,
    policy_for_backend,
)


@dataclass(slots=True, frozen=True)
class PoseQualityPolicyReport:
    backend: str
    minimum_visibility: float
    minimum_presence: float
    minimum_confidence: float | None
    calibration_version: str = "1.0.0"

    def to_dict(self) -> dict:
        return asdict(self)


def build_pose_quality_policy_report(
    backend: str,
    *,
    policy: LandmarkUsabilityPolicy | None = None,
) -> dict:
    active_policy = policy or policy_for_backend(backend)
    return PoseQualityPolicyReport(
        backend=backend.strip().lower(),
        minimum_visibility=active_policy.minimum_visibility,
        minimum_presence=active_policy.minimum_presence,
        minimum_confidence=active_policy.minimum_confidence,
    ).to_dict()
