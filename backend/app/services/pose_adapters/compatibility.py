from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.pose_adapters.models import (
    UnifiedPoseFrame,
)


@dataclass(slots=True, frozen=True)
class LegacyLandmark:
    x: float
    y: float
    z: float = 0.0
    visibility: float = 0.0
    presence: float = 0.0


def to_legacy_landmark_list(
    frame: UnifiedPoseFrame,
    *,
    index_map: dict[str, int],
    total_landmarks: int,
) -> list[Any]:
    """
    Compatibility bridge for existing biomechanics code that still
    expects an indexed landmark list.
    """

    landmarks: list[Any] = [
        LegacyLandmark(
            x=0.0,
            y=0.0,
        )
        for _ in range(total_landmarks)
    ]

    for keypoint in frame.keypoints:
        target_index = index_map.get(
            keypoint.name
        )

        if target_index is None:
            continue

        landmarks[target_index] = (
            LegacyLandmark(
                x=keypoint.x,
                y=keypoint.y,
                z=keypoint.z or 0.0,
                visibility=(
                    keypoint.visibility
                    if keypoint.visibility
                    is not None
                    else keypoint.confidence
                    or 0.0
                ),
                presence=(
                    keypoint.presence
                    if keypoint.presence
                    is not None
                    else keypoint.confidence
                    or 0.0
                ),
            )
        )

    return landmarks
