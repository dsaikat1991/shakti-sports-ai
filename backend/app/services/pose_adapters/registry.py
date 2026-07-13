from __future__ import annotations

from app.services.pose_adapters.base import PoseAdapter
from app.services.pose_adapters.mediapipe_adapter import (
    MediaPipePoseAdapter,
)
from app.services.pose_adapters.rtmpose_adapter import (
    RTMPoseAdapter,
)


class PoseAdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, PoseAdapter] = {}

    def register(
        self,
        adapter: PoseAdapter,
    ) -> None:
        self._adapters[
            adapter.backend_name
        ] = adapter

    def get(
        self,
        backend_name: str,
    ) -> PoseAdapter:
        try:
            return self._adapters[
                backend_name
            ]
        except KeyError as exc:
            raise KeyError(
                f"Pose adapter '{backend_name}' is not registered."
            ) from exc

    def available_backends(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            sorted(self._adapters)
        )


def create_default_registry(
) -> PoseAdapterRegistry:
    registry = PoseAdapterRegistry()
    registry.register(
        MediaPipePoseAdapter()
    )
    registry.register(
        RTMPoseAdapter()
    )
    return registry
