from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.services.pose_adapters.models import UnifiedPoseFrame


class PoseAdapter(ABC):
    backend_name: str = "unknown"

    @abstractmethod
    def adapt_frame(
        self,
        raw_pose: Any,
        *,
        frame_index: int,
        timestamp_ms: int,
        image_width: int | None = None,
        image_height: int | None = None,
    ) -> UnifiedPoseFrame:
        raise NotImplementedError
