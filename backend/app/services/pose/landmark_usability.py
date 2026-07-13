from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class LandmarkUsabilityPolicy:
    backend: str
    minimum_visibility: float
    minimum_presence: float
    minimum_confidence: float | None = None

    def normalized_backend(self) -> str:
        return self.backend.strip().lower()


MEDIAPIPE_POLICY = LandmarkUsabilityPolicy(
    backend="mediapipe",
    minimum_visibility=0.50,
    minimum_presence=0.50,
    minimum_confidence=None,
)

RTMPOSE_POLICY = LandmarkUsabilityPolicy(
    backend="rtmpose",
    minimum_visibility=0.35,
    minimum_presence=0.35,
    minimum_confidence=0.35,
)

DEFAULT_POLICY_BY_BACKEND = {
    "mediapipe": MEDIAPIPE_POLICY,
    "rtmpose": RTMPOSE_POLICY,
}


def policy_for_backend(backend: str | None) -> LandmarkUsabilityPolicy:
    normalized = backend.strip().lower() if backend else "mediapipe"
    return DEFAULT_POLICY_BY_BACKEND.get(normalized, MEDIAPIPE_POLICY)


def _read_numeric(value: Any, *, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _read_attribute(
    landmark: Any,
    name: str,
    *,
    default: float = 0.0,
) -> float:
    if isinstance(landmark, dict):
        return _read_numeric(landmark.get(name, default), default=default)
    return _read_numeric(getattr(landmark, name, default), default=default)


def landmark_confidence(
    landmark: Any,
    *,
    backend: str | None = None,
) -> float:
    normalized_backend = backend.strip().lower() if backend else "mediapipe"

    if normalized_backend == "rtmpose":
        direct_confidence = _read_attribute(
            landmark,
            "confidence",
            default=-1.0,
        )
        if direct_confidence >= 0.0:
            return direct_confidence

        visibility = _read_attribute(landmark, "visibility", default=0.0)
        presence = _read_attribute(landmark, "presence", default=visibility)
        return min(visibility, presence)

    visibility = _read_attribute(landmark, "visibility", default=0.0)
    presence = _read_attribute(landmark, "presence", default=visibility)
    return min(visibility, presence)


def landmark_is_usable(
    landmark: Any,
    *,
    backend: str | None = None,
    policy: LandmarkUsabilityPolicy | None = None,
    minimum_confidence: float | None = None,
    minimum_visibility: float | None = None,
    minimum_presence: float | None = None,
) -> bool:
    active_policy = policy or policy_for_backend(backend)
    normalized_backend = (
        backend.strip().lower()
        if backend
        else active_policy.normalized_backend()
    )

    if normalized_backend == "rtmpose":
        threshold = (
            minimum_confidence
            if minimum_confidence is not None
            else active_policy.minimum_confidence
            if active_policy.minimum_confidence is not None
            else min(
                active_policy.minimum_visibility,
                active_policy.minimum_presence,
            )
        )
        return landmark_confidence(landmark, backend="rtmpose") >= threshold

    visibility_threshold = (
        minimum_visibility
        if minimum_visibility is not None
        else minimum_confidence
        if minimum_confidence is not None
        else active_policy.minimum_visibility
    )
    presence_threshold = (
        minimum_presence
        if minimum_presence is not None
        else minimum_confidence
        if minimum_confidence is not None
        else active_policy.minimum_presence
    )

    visibility = _read_attribute(landmark, "visibility", default=0.0)
    presence = _read_attribute(landmark, "presence", default=visibility)
    return (
        visibility >= visibility_threshold
        and presence >= presence_threshold
    )


def filter_usable_landmarks(
    landmarks: dict[str, Any],
    *,
    backend: str | None = None,
    policy: LandmarkUsabilityPolicy | None = None,
) -> dict[str, Any]:
    return {
        name: landmark
        for name, landmark in landmarks.items()
        if landmark_is_usable(
            landmark,
            backend=backend,
            policy=policy,
        )
    }


def usability_summary(
    landmarks: dict[str, Any],
    *,
    backend: str | None = None,
    policy: LandmarkUsabilityPolicy | None = None,
) -> dict:
    active_policy = policy or policy_for_backend(backend)
    usable = filter_usable_landmarks(
        landmarks,
        backend=backend,
        policy=active_policy,
    )
    total = len(landmarks)
    usable_count = len(usable)
    return {
        "backend": backend or active_policy.backend,
        "minimum_visibility": active_policy.minimum_visibility,
        "minimum_presence": active_policy.minimum_presence,
        "minimum_confidence": active_policy.minimum_confidence,
        "total_landmarks": total,
        "usable_landmarks": usable_count,
        "usable_ratio": round(usable_count / total, 4) if total else 0.0,
    }
