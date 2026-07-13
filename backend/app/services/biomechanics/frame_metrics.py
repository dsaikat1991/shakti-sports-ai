from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class FrameMetrics:
    frame_index: int
    timestamp_ms: int

    joint_angles: dict[str, float | None]

    bounding_box: dict[str, Any] | None

    camera_view: dict[str, Any]

    landmarks: list[Any]