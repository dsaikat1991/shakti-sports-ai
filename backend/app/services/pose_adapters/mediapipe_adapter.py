from __future__ import annotations

from typing import Any

from app.services.pose_adapters.base import PoseAdapter
from app.services.pose_adapters.models import (
    UnifiedKeypoint,
    UnifiedPoseFrame,
)
from app.services.pose_adapters.skeleton import (
    MEDIAPIPE_INDEX_MAP,
)


def _value(
    landmark: Any,
    name: str,
    default: float | None = None,
) -> float | None:
    if isinstance(landmark, dict):
        value = landmark.get(name, default)
    else:
        value = getattr(landmark, name, default)

    if value is None:
        return None

    return float(value)


class MediaPipePoseAdapter(PoseAdapter):
    backend_name = "mediapipe"

    def adapt_frame(
        self,
        raw_pose: Any,
        *,
        frame_index: int,
        timestamp_ms: int,
        image_width: int | None = None,
        image_height: int | None = None,
    ) -> UnifiedPoseFrame:
        keypoints: list[UnifiedKeypoint] = []

        for source_index, name in MEDIAPIPE_INDEX_MAP.items():
            if source_index >= len(raw_pose):
                continue

            landmark = raw_pose[source_index]

            visibility = _value(
                landmark,
                "visibility",
            )

            presence = _value(
                landmark,
                "presence",
            )

            confidences = [
                value
                for value in (
                    visibility,
                    presence,
                )
                if value is not None
            ]

            confidence = (
                min(confidences)
                if confidences
                else None
            )

            keypoints.append(
                UnifiedKeypoint(
                    name=name,
                    x=float(_value(landmark, "x", 0.0)),
                    y=float(_value(landmark, "y", 0.0)),
                    z=_value(landmark, "z"),
                    visibility=visibility,
                    presence=presence,
                    confidence=confidence,
                    source_index=source_index,
                )
            )

        return UnifiedPoseFrame(
            backend="mediapipe",
            frame_index=frame_index,
            timestamp_ms=timestamp_ms,
            keypoints=tuple(keypoints),
            image_width=image_width,
            image_height=image_height,
            metadata={
                "source_landmark_count": len(raw_pose),
            },
        )
