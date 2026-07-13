from __future__ import annotations
import numpy as np
from app.services.motion.models import PointMotionState, PointSample, ScalarMotionState, ScalarSample

def _validate_timestamps(timestamps_ms: list[int]) -> None:
    for i in range(1, len(timestamps_ms)):
        if timestamps_ms[i] <= timestamps_ms[i-1]:
            raise ValueError("Timestamps must be strictly increasing.")

def _smooth(values: list[float], window_size: int = 5) -> list[float]:
    if len(values) < 3 or window_size <= 1:
        return values.copy()
    if window_size % 2 == 0:
        window_size += 1
    r = window_size // 2
    return [float(np.mean(values[max(0,i-r):min(len(values),i+r+1)])) for i in range(len(values))]

def _gradient(values: list[float], timestamps_ms: list[int]) -> list[float]:
    if not values:
        return []
    if len(values) == 1:
        return [0.0]
    t = np.asarray(timestamps_ms, dtype=float) / 1000.0
    return [float(v) for v in np.gradient(np.asarray(values, dtype=float), t, edge_order=1)]

def compute_scalar_motion(samples: list[ScalarSample], *, smoothing_window: int = 5) -> list[ScalarMotionState]:
    if not samples:
        return []
    ordered = sorted(samples, key=lambda s: s.timestamp_ms)
    timestamps = [s.timestamp_ms for s in ordered]
    _validate_timestamps(timestamps)
    values = _smooth([float(s.value) for s in ordered], smoothing_window)
    velocity = _gradient(values, timestamps)
    acceleration = _gradient(velocity, timestamps)
    jerk = _gradient(acceleration, timestamps)
    return [
        ScalarMotionState(
            frame_index=s.frame_index,
            timestamp_ms=s.timestamp_ms,
            value=round(values[i],6),
            velocity=round(velocity[i],6),
            acceleration=round(acceleration[i],6),
            jerk=round(jerk[i],6),
            confidence=round(max(0.0,min(1.0,s.confidence)),4),
        )
        for i,s in enumerate(ordered)
    ]

def compute_point_motion(samples: list[PointSample], *, smoothing_window: int = 5) -> list[PointMotionState]:
    if not samples:
        return []
    ordered = sorted(samples, key=lambda s: s.timestamp_ms)
    timestamps = [s.timestamp_ms for s in ordered]
    _validate_timestamps(timestamps)
    xs = _smooth([float(s.x) for s in ordered], smoothing_window)
    ys = _smooth([float(s.y) for s in ordered], smoothing_window)
    vx, vy = _gradient(xs,timestamps), _gradient(ys,timestamps)
    ax, ay = _gradient(vx,timestamps), _gradient(vy,timestamps)
    jx, jy = _gradient(ax,timestamps), _gradient(ay,timestamps)
    out = []
    for i,s in enumerate(ordered):
        speed = (vx[i]**2 + vy[i]**2)**0.5
        amag = (ax[i]**2 + ay[i]**2)**0.5
        jmag = (jx[i]**2 + jy[i]**2)**0.5
        out.append(PointMotionState(
            frame_index=s.frame_index, timestamp_ms=s.timestamp_ms,
            x=round(xs[i],6), y=round(ys[i],6),
            velocity_x=round(vx[i],6), velocity_y=round(vy[i],6), speed=round(speed,6),
            acceleration_x=round(ax[i],6), acceleration_y=round(ay[i],6),
            acceleration_magnitude=round(amag,6),
            jerk_x=round(jx[i],6), jerk_y=round(jy[i],6),
            jerk_magnitude=round(jmag,6),
            confidence=round(max(0.0,min(1.0,s.confidence)),4),
        ))
    return out
