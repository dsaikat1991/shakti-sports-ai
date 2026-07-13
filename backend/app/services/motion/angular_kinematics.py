from __future__ import annotations
from app.services.motion.derivatives import compute_scalar_motion
from app.services.motion.models import ScalarMotionState, ScalarSample

def unwrap_degrees(values: list[float]) -> list[float]:
    if not values:
        return []
    result = [float(values[0])]
    for value in values[1:]:
        candidate = float(value)
        previous = result[-1]
        while candidate - previous > 180.0:
            candidate -= 360.0
        while candidate - previous < -180.0:
            candidate += 360.0
        result.append(candidate)
    return result

def compute_angular_motion(samples: list[ScalarSample], *, smoothing_window: int = 5, unwrap: bool = True) -> list[ScalarMotionState]:
    if not samples:
        return []
    ordered = sorted(samples, key=lambda s: s.timestamp_ms)
    values = unwrap_degrees([s.value for s in ordered]) if unwrap else [s.value for s in ordered]
    prepared = [
        ScalarSample(s.frame_index, s.timestamp_ms, values[i], s.confidence)
        for i,s in enumerate(ordered)
    ]
    return compute_scalar_motion(prepared, smoothing_window=smoothing_window)
