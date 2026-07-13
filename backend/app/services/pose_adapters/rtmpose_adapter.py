from __future__ import annotations

from typing import Any

from app.services.pose_adapters.base import PoseAdapter
from app.services.pose_adapters.models import (
    UnifiedKeypoint,
    UnifiedPoseFrame,
)


DEFAULT_RTMPOSE_NAME_MAP: dict[int, str] = {
    0: "nose",
    1: "left_eye",
    2: "right_eye",
    3: "left_ear",
    4: "right_ear",
    5: "left_shoulder",
    6: "right_shoulder",
    7: "left_elbow",
    8: "right_elbow",
    9: "left_wrist",
    10: "right_wrist",
    11: "left_hip",
    12: "right_hip",
    13: "left_knee",
    14: "right_knee",
    15: "left_ankle",
    16: "right_ankle",
}


class RTMPoseAdapter(PoseAdapter):
    backend_name = "rtmpose"

    def __init__(
        self,
        *,
        name_map: dict[int, str] | None = None,
    ) -> None:
        self.name_map = (
            name_map
            or DEFAULT_RTMPOSE_NAME_MAP
        )

    def adapt_frame(
        self,
        raw_pose: Any,
        *,
        frame_index: int,
        timestamp_ms: int,
        image_width: int | None = None,
        image_height: int | None = None,
    ) -> UnifiedPoseFrame:
        keypoints_data = raw_pose["keypoints"]
        scores = raw_pose.get(
            "keypoint_scores",
            [],
        )

        keypoints: list[UnifiedKeypoint] = []

        for source_index, name in self.name_map.items():
            if source_index >= len(keypoints_data):
                continue

            coordinates = keypoints_data[source_index]

            confidence = (
                float(scores[source_index])
                if source_index < len(scores)
                else None
            )

            keypoints.append(
                UnifiedKeypoint(
                    name=name,
                    x=float(coordinates[0]),
                    y=float(coordinates[1]),
                    z=(
                        float(coordinates[2])
                        if len(coordinates) > 2
                        else None
                    ),
                    confidence=confidence,
                    source_index=source_index,
                )
            )

        return UnifiedPoseFrame(
            backend="rtmpose",
            frame_index=frame_index,
            timestamp_ms=timestamp_ms,
            keypoints=tuple(keypoints),
            image_width=image_width,
            image_height=image_height,
            metadata={
                "source_landmark_count": (
                    len(keypoints_data)
                ),
                "custom_schema": (
                    self.name_map
                    != DEFAULT_RTMPOSE_NAME_MAP
                ),
            },
        )
