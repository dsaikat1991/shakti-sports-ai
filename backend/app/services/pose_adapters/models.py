from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


PoseBackend = Literal[
    "mediapipe",
    "rtmpose",
    "deeplabcut",
    "unknown",
]


@dataclass(slots=True, frozen=True)
class UnifiedKeypoint:
    name: str
    x: float
    y: float
    z: float | None = None
    visibility: float | None = None
    presence: float | None = None
    confidence: float | None = None
    source_index: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class UnifiedPoseFrame:
    backend: PoseBackend
    frame_index: int
    timestamp_ms: int
    keypoints: tuple[UnifiedKeypoint, ...]
    skeleton_name: str = "shakti_unified_v1"
    image_width: int | None = None
    image_height: int | None = None
    metadata: dict[str, Any] | None = None

    def keypoint_map(self) -> dict[str, UnifiedKeypoint]:
        return {
            keypoint.name: keypoint
            for keypoint in self.keypoints
        }

    def get(self, name: str) -> UnifiedKeypoint | None:
        return self.keypoint_map().get(name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "frame_index": self.frame_index,
            "timestamp_ms": self.timestamp_ms,
            "skeleton_name": self.skeleton_name,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "metadata": self.metadata or {},
            "keypoints": [
                keypoint.to_dict()
                for keypoint in self.keypoints
            ],
        }
