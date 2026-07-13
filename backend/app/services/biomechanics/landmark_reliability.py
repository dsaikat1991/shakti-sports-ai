from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any
import numpy as np

from app.services.biomechanics.frame_metrics import FrameMetrics

DEFAULT_LANDMARK_NAMES = {
    23: "left_hip", 24: "right_hip", 25: "left_knee", 26: "right_knee",
    27: "left_ankle", 28: "right_ankle", 29: "left_heel", 30: "right_heel",
    31: "left_foot_index", 32: "right_foot_index",
}

@dataclass(slots=True, frozen=True)
class LandmarkReliability:
    landmark_index: int
    landmark_name: str
    frame_index: int
    timestamp_ms: int
    visibility_score: float
    presence_score: float
    frame_bounds_score: float
    motion_consistency_score: float
    trajectory_consistency_score: float
    occlusion_risk_score: float
    overall_score: float
    rating: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def _value(landmark: Any, name: str, default: float = 0.0) -> float:
    if isinstance(landmark, dict):
        return float(landmark.get(name, default))
    return float(getattr(landmark, name, default))

def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))

def _bounds_score(x: float, y: float, margin: float = 0.03) -> float:
    if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
        return 0.0
    distance = min(x, 1.0 - x, y, 1.0 - y)
    return 1.0 if distance >= margin else _clamp(distance / margin)

def _distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

def _rating(score: float) -> str:
    if score >= 0.90: return "very_high"
    if score >= 0.80: return "high"
    if score >= 0.65: return "moderate"
    if score >= 0.50: return "low"
    return "very_low"

def _motion_consistency(previous, current, following) -> float:
    if previous is None or following is None:
        return 0.75
    expected = ((previous[0] + following[0]) / 2.0, (previous[1] + following[1]) / 2.0)
    return _clamp(1.0 - _distance(current, expected) / 0.08)

def _trajectory_consistency(points: list[tuple[float, float]]) -> float:
    if len(points) < 3:
        return 0.75
    steps = [_distance(points[i - 1], points[i]) for i in range(1, len(points))]
    avg = float(np.mean(steps))
    if avg <= 1e-9:
        return 1.0
    return _clamp(1.0 - float(np.std(steps)) / avg)

def evaluate_landmark_reliability(
    frame_metrics: list[FrameMetrics],
    landmark_index: int,
    *,
    landmark_name: str | None = None,
    history_window: int = 5,
) -> list[LandmarkReliability]:
    name = landmark_name or DEFAULT_LANDMARK_NAMES.get(landmark_index, f"landmark_{landmark_index}")
    points: list[tuple[float, float] | None] = []
    raw: list[Any | None] = []

    for frame in frame_metrics:
        if landmark_index >= len(frame.landmarks):
            points.append(None); raw.append(None); continue
        landmark = frame.landmarks[landmark_index]
        x, y = _value(landmark, "x", -1.0), _value(landmark, "y", -1.0)
        points.append((x, y) if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0 else None)
        raw.append(landmark)

    results: list[LandmarkReliability] = []
    for index, frame in enumerate(frame_metrics):
        landmark, point = raw[index], points[index]
        if landmark is None or point is None:
            visibility = presence = bounds = motion = trajectory = overall = 0.0
            occlusion = 1.0
        else:
            visibility = _clamp(_value(landmark, "visibility", 0.0))
            presence = _clamp(_value(landmark, "presence", 0.0))
            bounds = _bounds_score(*point)
            previous = points[index - 1] if index > 0 else None
            following = points[index + 1] if index < len(points) - 1 else None
            motion = _motion_consistency(previous, point, following)
            start = max(0, index - history_window + 1)
            recent = [item for item in points[start:index + 1] if item is not None]
            trajectory = _trajectory_consistency(recent)
            occlusion = _clamp((1 - visibility) * 0.4 + (1 - presence) * 0.3 + (1 - bounds) * 0.15 + (1 - motion) * 0.15)
            overall = _clamp((visibility * 0.24 + presence * 0.20 + bounds * 0.12 + motion * 0.22 + trajectory * 0.22) * (1.0 - occlusion * 0.35))
        results.append(LandmarkReliability(
            landmark_index, name, frame.frame_index, frame.timestamp_ms,
            round(visibility, 4), round(presence, 4), round(bounds, 4),
            round(motion, 4), round(trajectory, 4), round(occlusion, 4),
            round(overall, 4), _rating(overall),
        ))
    return results

def summarize_landmark_reliability(items: list[LandmarkReliability]) -> dict[str, Any]:
    if not items:
        return {"status": "insufficient_data", "frames": 0, "average_score": None, "minimum_score": None, "coverage_above_moderate_percent": None, "average_occlusion_risk": None}
    scores = [item.overall_score for item in items]
    risks = [item.occlusion_risk_score for item in items]
    return {
        "status": "completed",
        "frames": len(items),
        "average_score": round(mean(scores) * 100.0, 2),
        "minimum_score": round(min(scores) * 100.0, 2),
        "coverage_above_moderate_percent": round(sum(score >= 0.65 for score in scores) / len(scores) * 100.0, 2),
        "average_occlusion_risk": round(mean(risks) * 100.0, 2),
    }
